"""Chat efêmero por ponto histórico (WebSocket).

Conexão:  ws(s)://<host>/v1/chat/{landmark_id}?token=<jwt>&lat=<lat>&lon=<lon>
          (o token também pode ir no header `Authorization: Bearer <jwt>`)

Regras:
- só usuários autenticados;
- o ponto precisa existir e estar aprovado;
- o usuário precisa estar a até CHAT_JOIN_RADIUS_M metros do ponto para entrar
  e é desconectado se informar posição além de CHAT_LEAVE_RADIUS_M.

Cliente -> servidor (JSON):
  {"type": "message", "text": "..."}
  {"type": "location", "lat": -22.5, "lon": -41.9}
  {"type": "ping"}

Servidor -> cliente (JSON):
  {"type": "welcome", ...}      ao entrar
  {"type": "message", "id", "room", "user": {"id", "name"}, "text", "sent_at"}
  {"type": "presence", "event": "join"|"leave", "room", "user", "sent_at"}
  {"type": "error", "code", "message"}
  {"type": "pong"}

Códigos de fechamento: 4400 parâmetros inválidos, 4401 não autenticado,
4403 fora do raio, 4404 ponto inexistente.
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query, Request, WebSocket, WebSocketDisconnect

from app.api.deps import CurrentUser, Db, resolve_user_from_token
from app.chat.geo import haversine_m
from app.chat.hub import Connection
from app.core.config import get_settings
from app.core.errors import AppError, Forbidden, NotFound
from app.db.mongo import get_database
from app.models.common import ModerationStatus
from app.models.user import Plan
from app.repositories import landmarks as landmarks_repo
from app.repositories.common import parse_object_id, user_summary, utcnow

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger("hist.chat")

CLOSE_BAD_REQUEST = 4400
CLOSE_UNAUTHORIZED = 4401
CLOSE_OUT_OF_RANGE = 4403
CLOSE_NOT_FOUND = 4404


async def _reject(ws: WebSocket, close_code: int, code: str, message: str) -> None:
    await ws.send_json({"type": "error", "code": code, "message": message})
    await ws.close(code=close_code, reason=message[:120])


def _token_from(ws: WebSocket, token: str | None) -> str | None:
    if token:
        return token
    auth = ws.headers.get("authorization", "")
    scheme, _, value = auth.partition(" ")
    return value if scheme.lower() == "bearer" and value else None


def _parse_coord(value, low: float, high: float) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if low <= number <= high else None


@router.websocket("/{landmark_id}")
async def chat_socket(
    websocket: WebSocket,
    landmark_id: str,
    token: str | None = None,
    lat: str | None = None,
    lon: str | None = None,
):
    settings = get_settings()
    hub = websocket.app.state.chat_hub
    store = websocket.app.state.chat_store
    db = get_database()

    # Aceita primeiro para conseguir explicar ao app o motivo de uma recusa.
    await websocket.accept()

    try:
        user = await resolve_user_from_token(db, _token_from(websocket, token))
    except AppError as exc:
        return await _reject(websocket, CLOSE_UNAUTHORIZED, exc.code, exc.message)

    latitude, longitude = _parse_coord(lat, -90, 90), _parse_coord(lon, -180, 180)
    if latitude is None or longitude is None:
        return await _reject(websocket, CLOSE_BAD_REQUEST, "invalid_location",
                             "Informe lat e lon válidos para entrar no chat.")

    try:
        landmark = await landmarks_repo.get(db, parse_object_id(landmark_id))
    except NotFound:
        landmark = None
    if landmark is None or landmark["status"] != ModerationStatus.APPROVED.value:
        return await _reject(websocket, CLOSE_NOT_FOUND, "not_found", "Ponto histórico não encontrado.")

    lm_lon, lm_lat = landmark["location"]["coordinates"]
    distance = haversine_m(latitude, longitude, lm_lat, lm_lon)
    if distance > settings.CHAT_JOIN_RADIUS_M:
        return await _reject(
            websocket, CLOSE_OUT_OF_RANGE, "out_of_range",
            f"Você precisa estar a até {settings.CHAT_JOIN_RADIUS_M} m do ponto "
            f"(distância atual: {distance:.0f} m).",
        )

    room = str(landmark["_id"])
    author = user_summary(user)
    conn = Connection(websocket=websocket, room=room, user_id=author["id"], user_name=author["name"],
                      latitude=latitude, longitude=longitude)
    hub.join(conn)
    try:
        await websocket.send_json({
            "type": "welcome",
            "room": room,
            "landmark": {"id": room, "name": landmark["name"]},
            "user": author,
            "join_radius_m": settings.CHAT_JOIN_RADIUS_M,
            "leave_radius_m": settings.CHAT_LEAVE_RADIUS_M,
            "max_message_length": settings.CHAT_MAX_MESSAGE_LENGTH,
            "history_enabled": store.enabled,
        })
        await hub.publish(room, _presence("join", room, author))
        await _receive_loop(websocket, conn, hub, store, user, (lm_lat, lm_lon))
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("Erro inesperado no chat da sala %s", room)
    finally:
        hub.leave(conn)
        try:
            await hub.publish(room, _presence("leave", room, author))
        except Exception:
            logger.exception("Falha ao anunciar saída na sala %s", room)


async def _receive_loop(websocket, conn: Connection, hub, store, user: dict, landmark_pos) -> None:
    settings = get_settings()
    while True:
        raw = await websocket.receive_text()
        try:
            data = json.loads(raw)
            kind = data.get("type")
        except (ValueError, AttributeError):
            await _error(websocket, "invalid_payload", "Envie um JSON com o campo 'type'.")
            continue

        if kind == "ping":
            await websocket.send_json({"type": "pong"})

        elif kind == "location":
            latitude = _parse_coord(data.get("lat"), -90, 90)
            longitude = _parse_coord(data.get("lon"), -180, 180)
            if latitude is None or longitude is None:
                await _error(websocket, "invalid_location", "lat/lon inválidos.")
                continue
            conn.latitude, conn.longitude = latitude, longitude
            distance = haversine_m(latitude, longitude, *landmark_pos)
            if distance > settings.CHAT_LEAVE_RADIUS_M:
                await _reject(websocket, CLOSE_OUT_OF_RANGE, "out_of_range",
                              f"Você se afastou do ponto ({distance:.0f} m).")
                return

        elif kind == "message":
            text = data.get("text")
            if not isinstance(text, str) or not text.strip():
                await _error(websocket, "invalid_message", "Mensagem vazia.")
                continue
            text = text.strip()
            if len(text) > settings.CHAT_MAX_MESSAGE_LENGTH:
                await _error(websocket, "message_too_long",
                             f"Limite de {settings.CHAT_MAX_MESSAGE_LENGTH} caracteres.")
                continue
            if not conn.allow_message(settings.CHAT_RATE_LIMIT_MESSAGES, settings.CHAT_RATE_LIMIT_WINDOW_S):
                await _error(websocket, "rate_limited", "Muitas mensagens em pouco tempo. Aguarde um pouco.")
                continue
            event = {
                "type": "message",
                "id": uuid.uuid4().hex,
                "room": conn.room,
                "user": {"id": conn.user_id, "name": conn.user_name},
                "text": text,
                "sent_at": utcnow().isoformat(),
            }
            await store.save(event, user["_id"])
            await hub.publish(conn.room, event)

        else:
            await _error(websocket, "unknown_type", "Tipo de evento desconhecido.")


async def _error(websocket: WebSocket, code: str, message: str) -> None:
    await websocket.send_json({"type": "error", "code": code, "message": message})


def _presence(event: str, room: str, user: dict) -> dict:
    return {"type": "presence", "event": event, "room": room, "user": user, "sent_at": utcnow().isoformat()}


@router.get(
    "/{landmark_id}/messages",
    summary="Histórico do chat (plano premium)",
    description="Disponível apenas com `CHAT_PERSISTENCE_ENABLED=true` e para usuários com plano premium. "
    "Hoje o recurso está desativado e responde 404 `feature_disabled`.",
)
async def chat_history(
    request: Request,
    landmark_id: str,
    user: CurrentUser,
    db: Db,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    before: Annotated[datetime | None, Query(description="Mensagens anteriores a este instante (ISO 8601).")] = None,
):
    store = request.app.state.chat_store
    if not store.enabled:
        raise NotFound("Histórico de chat indisponível.", code="feature_disabled")
    if user.get("plan") != Plan.PREMIUM.value:
        raise Forbidden("Recurso exclusivo do plano premium.", code="premium_required")
    landmark = await landmarks_repo.get(db, parse_object_id(landmark_id, "Ponto histórico"))
    if landmark is None or landmark["status"] != ModerationStatus.APPROVED.value:
        raise NotFound("Ponto histórico não encontrado.")
    return {"items": await store.history(str(landmark["_id"]), limit=limit, before=before)}
