from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.db.mongo import get_database

router = APIRouter(tags=["Saúde"])


@router.get("/health", summary="Verificação de saúde (usada pelo deploy)")
async def health(request: Request):
    checks = {}
    try:
        await get_database().client.admin.command("ping")
        checks["mongo"] = "ok"
    except Exception:
        checks["mongo"] = "error"
    broker = request.app.state.chat_hub.broker
    checks["chat_broker"] = type(broker).__name__
    if type(broker).__name__ == "InMemoryBroker":
        checks["redis"] = "disabled"
    else:
        checks["redis"] = "ok" if await broker.ping() else "error"
    healthy = all(v != "error" for v in checks.values())
    return JSONResponse({"status": "ok" if healthy else "degraded", **checks}, status_code=200 if healthy else 503)
