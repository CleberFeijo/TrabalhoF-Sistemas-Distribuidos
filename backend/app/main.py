from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, chat, curiosities, health, landmarks, moderation, users
from app.bootstrap import ensure_admin
from app.chat.broker import build_broker
from app.chat.hub import ChatHub
from app.chat.store import build_store
from app.core.config import Environment, get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.db import mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    db = await mongo.connect()
    await ensure_admin(db)
    app.state.chat_store = build_store(settings.CHAT_PERSISTENCE_ENABLED, db)
    app.state.chat_hub = ChatHub(build_broker(settings.REDIS_URL))
    await app.state.chat_hub.start()
    try:
        yield
    finally:
        await app.state.chat_hub.stop()
        await mongo.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(debug=settings.ENV == Environment.DEVELOPMENT)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API do Hist — descoberta de patrimônio histórico urbano por geolocalização.",
        lifespan=lifespan,
        docs_url="/docs" if settings.DOCS_ENABLED else None,
        redoc_url="/redoc" if settings.DOCS_ENABLED else None,
        openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
    )
    register_error_handlers(app)

    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    v1 = APIRouter(prefix="/v1")
    for module in (auth, users, landmarks, curiosities, moderation, chat):
        v1.include_router(module.router)
    app.include_router(v1)
    app.include_router(health.router)

    @app.get("/", include_in_schema=False)
    async def root():
        return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "docs": app.docs_url}

    return app


app = create_app()
