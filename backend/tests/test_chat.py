import asyncio
import os

import pytest
from bson import ObjectId
from starlette.websockets import WebSocketDisconnect

from tests.conftest import BASE_LAT, BASE_LON, Api, offset


def _url(lid: str, token: str | None = None, lat=BASE_LAT, lon=BASE_LON) -> str:
    params = []
    if token:
        params.append(f"token={token}")
    if lat is not None:
        params.append(f"lat={lat}")
    if lon is not None:
        params.append(f"lon={lon}")
    return f"/v1/chat/{lid}?" + "&".join(params)


def _expect_rejection(api: Api, url: str, code: str, close_code: int, headers=None):
    with api.c.websocket_connect(url, headers=headers or {}) as ws:
        event = ws.receive_json()
        assert event["type"] == "error" and event["code"] == code, event
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
        assert exc.value.code == close_code


def test_chat_requires_valid_token(api: Api):
    lid = api.landmark()
    _expect_rejection(api, _url(lid), "unauthorized", 4401)
    _expect_rejection(api, _url(lid, "token-falso"), "unauthorized", 4401)


def test_chat_accepts_token_in_header(api: Api):
    user = api.register()
    lid = api.landmark()
    with api.c.websocket_connect(_url(lid), headers=user["headers"]) as ws:
        assert ws.receive_json()["type"] == "welcome"


def test_chat_rejects_missing_location_missing_landmark_and_far_users(api: Api):
    user = api.register()
    token = user["access_token"]
    lid = api.landmark()
    pending = api.landmark(status="pending")
    _expect_rejection(api, _url(lid, token, lat=None), "invalid_location", 4400)
    _expect_rejection(api, _url(lid, token, lat="abc"), "invalid_location", 4400)
    _expect_rejection(api, _url(pending, token), "not_found", 4404)
    _expect_rejection(api, _url(str(ObjectId()), token), "not_found", 4404)
    _expect_rejection(api, _url("invalido", token), "not_found", 4404)
    far_lat, _ = offset(BASE_LAT, BASE_LON, north_m=250)
    _expect_rejection(api, _url(lid, token, lat=far_lat), "out_of_range", 4403)


def test_chat_broadcast_uses_identity_from_token(api: Api):
    ana = api.register(name="Ana")
    bia = api.register(name="Bia")
    lid = api.landmark()
    near_lat, _ = offset(BASE_LAT, BASE_LON, north_m=180)
    with api.c.websocket_connect(_url(lid, ana["access_token"])) as wa:
        welcome = wa.receive_json()
        assert welcome["type"] == "welcome" and welcome["landmark"]["id"] == lid
        assert welcome["history_enabled"] is False
        assert wa.receive_json() == {**wa_join(welcome)}  # própria entrada também é anunciada

        with api.c.websocket_connect(_url(lid, bia["access_token"], lat=near_lat)) as wb:
            assert wb.receive_json()["type"] == "welcome"
            joined = wa.receive_json()
            assert joined["type"] == "presence" and joined["event"] == "join"
            assert joined["user"]["name"] == "Bia Teste"
            wb.receive_json()  # própria presença

            wa.send_json({"type": "message", "text": "  Olá, alguém aí?  ", "user": "impostor"})
            for ws in (wa, wb):
                msg = ws.receive_json()
                assert msg["type"] == "message"
                assert msg["text"] == "Olá, alguém aí?"
                assert msg["user"] == {"id": ana["user"]["id"], "name": "Ana Teste"}

            wb.send_json({"type": "ping"})
            assert wb.receive_json() == {"type": "pong"}

        left = wa.receive_json()
        assert left["type"] == "presence" and left["event"] == "leave" and left["user"]["name"] == "Bia Teste"


def wa_join(welcome: dict) -> dict:
    # helper: o evento de presença do próprio usuário é igual ao anunciado aos outros
    return {"type": "presence", "event": "join", "room": welcome["room"], "user": welcome["user"],
            "sent_at": _ANY}


class _Any:
    def __eq__(self, other):
        return True


_ANY = _Any()


def test_chat_isolated_per_landmark(api: Api):
    ana = api.register()
    bia = api.register()
    l1 = api.landmark(name="Um")
    l2 = api.landmark(name="Dois", lat=offset(BASE_LAT, BASE_LON, north_m=10)[0])
    with api.c.websocket_connect(_url(l1, ana["access_token"])) as wa, \
         api.c.websocket_connect(_url(l2, bia["access_token"])) as wb:
        wa.receive_json(), wa.receive_json()
        wb.receive_json(), wb.receive_json()
        wa.send_json({"type": "message", "text": "só sala um"})
        assert wa.receive_json()["text"] == "só sala um"
        wb.send_json({"type": "ping"})
        assert wb.receive_json() == {"type": "pong"}, "a sala dois não pode receber a mensagem da sala um"


def test_chat_validates_messages_and_rate_limits(api: Api):
    user = api.register()
    lid = api.landmark()
    with api.c.websocket_connect(_url(lid, user["access_token"])) as ws:
        ws.receive_json(), ws.receive_json()
        ws.send_text("isso não é json")
        assert ws.receive_json()["code"] == "invalid_payload"
        ws.send_json({"type": "message", "text": "   "})
        assert ws.receive_json()["code"] == "invalid_message"
        ws.send_json({"type": "message", "text": "x" * 1001})
        assert ws.receive_json()["code"] == "message_too_long"
        ws.send_json({"type": "dance"})
        assert ws.receive_json()["code"] == "unknown_type"
        for i in range(5):
            ws.send_json({"type": "message", "text": f"msg {i}"})
            assert ws.receive_json()["text"] == f"msg {i}"
        ws.send_json({"type": "message", "text": "uma a mais"})
        assert ws.receive_json()["code"] == "rate_limited"


def test_moving_away_disconnects(api: Api):
    user = api.register()
    lid = api.landmark()
    with api.c.websocket_connect(_url(lid, user["access_token"])) as ws:
        ws.receive_json(), ws.receive_json()
        lat_250, _ = offset(BASE_LAT, BASE_LON, north_m=250)
        ws.send_json({"type": "location", "lat": lat_250, "lon": BASE_LON})  # dentro da folga (300 m)
        ws.send_json({"type": "ping"})
        assert ws.receive_json() == {"type": "pong"}
        lat_400, _ = offset(BASE_LAT, BASE_LON, north_m=400)
        ws.send_json({"type": "location", "lat": lat_400, "lon": BASE_LON})
        assert ws.receive_json()["code"] == "out_of_range"
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
        assert exc.value.code == 4403


def test_history_is_disabled_by_default(api: Api):
    user = api.register()
    lid = api.landmark()
    r = api.c.get(f"/v1/chat/{lid}/messages", headers=user["headers"])
    assert r.status_code == 404 and r.json()["error"]["code"] == "feature_disabled"


def test_history_when_premium_persistence_enabled(raw_db, settings_env):
    from fastapi.testclient import TestClient

    from app.main import create_app

    for name in raw_db.list_collection_names():
        raw_db[name].delete_many({})
    settings_env(CHAT_PERSISTENCE_ENABLED="true")
    with TestClient(create_app()) as c:
        api = Api(c, raw_db)
        free = api.register()
        premium = api.register()
        raw_db.users.update_one({"_id": ObjectId(premium["user"]["id"])}, {"$set": {"plan": "premium"}})
        lid = api.landmark()
        with c.websocket_connect(_url(lid, free["access_token"])) as ws:
            assert ws.receive_json()["history_enabled"] is True
            ws.receive_json()
            for text in ("primeira", "segunda"):
                ws.send_json({"type": "message", "text": text})
                ws.receive_json()
        r = c.get(f"/v1/chat/{lid}/messages", headers=free["headers"])
        assert r.status_code == 403 and r.json()["error"]["code"] == "premium_required"
        r = c.get(f"/v1/chat/{lid}/messages", headers=premium["headers"])
        assert r.status_code == 200
        assert [m["text"] for m in r.json()["items"]] == ["primeira", "segunda"]


@pytest.mark.skipif(not os.environ.get("REDIS_URL_TEST"), reason="defina REDIS_URL_TEST para testar o Redis")
def test_redis_broker_delivers_between_processes():
    """Dois hubs com conexões Redis independentes simulam dois processos da API."""
    from app.chat.broker import RedisBroker

    async def scenario():
        received_a, received_b = [], []

        async def handler_a(room, event):
            received_a.append((room, event))

        async def handler_b(room, event):
            received_b.append((room, event))

        a, b = RedisBroker(os.environ["REDIS_URL_TEST"]), RedisBroker(os.environ["REDIS_URL_TEST"])
        await a.start(handler_a)
        await b.start(handler_b)
        try:
            await asyncio.sleep(0.2)
            await a.publish("sala-x", {"type": "message", "text": "via redis"})
            for _ in range(50):
                if received_a and received_b:
                    break
                await asyncio.sleep(0.05)
        finally:
            await a.stop()
            await b.stop()
        assert received_b == [("sala-x", {"type": "message", "text": "via redis"})]
        assert received_a == received_b

    asyncio.run(scenario())
