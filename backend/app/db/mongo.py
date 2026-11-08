"""Conexão assíncrona com o MongoDB (API async nativa do PyMongo)."""
import logging

from pymongo import ASCENDING, DESCENDING, GEOSPHERE, AsyncMongoClient, IndexModel
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import OperationFailure

from app.core.config import get_settings

logger = logging.getLogger("hist.db")

_client: AsyncMongoClient | None = None


async def connect() -> AsyncDatabase:
    global _client
    settings = get_settings()
    _client = AsyncMongoClient(settings.MONGO_URI, tz_aware=True, uuidRepresentation="standard")
    await _client.admin.command("ping")
    db = _client[settings.MONGO_DB]
    await ensure_indexes(db)
    logger.info("MongoDB conectado (banco '%s').", settings.MONGO_DB)
    return db


async def disconnect() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None


def get_database() -> AsyncDatabase:
    if _client is None:
        raise RuntimeError("MongoDB não inicializado.")
    return _client[get_settings().MONGO_DB]


async def ensure_indexes(db: AsyncDatabase) -> None:
    """Cria os índices de forma idempotente (seguro rodar a cada boot)."""
    settings = get_settings()
    await db.users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True, name="email_unique"),
    ])
    await db.landmarks.create_indexes([
        IndexModel([("location", GEOSPHERE)], name="location_2dsphere"),
        IndexModel([("status", ASCENDING), ("created_at", DESCENDING)], name="status_created"),
        IndexModel([("created_by", ASCENDING)], name="created_by"),
        # Evita duplicar pontos vindos do crawler (ex.: mesmo item da Wikidata).
        IndexModel(
            [("source.name", ASCENDING), ("source.external_id", ASCENDING)],
            unique=True,
            partialFilterExpression={"source.external_id": {"$type": "string"}},
            name="source_external_unique",
        ),
    ])
    await db.curiosities.create_indexes([
        IndexModel(
            [("landmark_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
            name="landmark_status_created",
        ),
        IndexModel([("status", ASCENDING), ("created_at", ASCENDING)], name="status_created"),
        IndexModel([("author_id", ASCENDING)], name="author"),
        IndexModel(
            [("source.name", ASCENDING), ("source.external_id", ASCENDING)],
            unique=True,
            partialFilterExpression={"source.external_id": {"$type": "string"}},
            name="source_external_unique",
        ),
    ])
    await db.chat_messages.create_indexes([
        IndexModel([("room_id", ASCENDING), ("sent_at", DESCENDING)], name="room_sent"),
    ])
    ttl = settings.CHAT_HISTORY_RETENTION_DAYS * 86400
    try:
        await db.chat_messages.create_index(
            [("sent_at", ASCENDING)], expireAfterSeconds=ttl, name="ttl_sent_at"
        )
    except OperationFailure as exc:
        # Retenção alterada desde a criação do índice: atualiza o TTL no lugar.
        if exc.code not in (85, 86):
            raise
        await db.command(
            "collMod", "chat_messages",
            index={"name": "ttl_sent_at", "expireAfterSeconds": ttl},
        )
