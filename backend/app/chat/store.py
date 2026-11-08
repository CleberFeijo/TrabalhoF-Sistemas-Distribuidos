"""Persistência de mensagens do chat (recurso do futuro plano premium).

Por padrão o chat é efêmero: `NullMessageStore` descarta tudo. Com
`CHAT_PERSISTENCE_ENABLED=true`, `MongoMessageStore` grava as mensagens
(com expiração via índice TTL) e o histórico fica disponível para usuários
com plano premium em `GET /v1/chat/{landmark_id}/messages`.
"""
from datetime import datetime

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase


class NullMessageStore:
    enabled = False

    async def save(self, event: dict, user_id: ObjectId) -> None:
        return None

    async def history(self, room_id: str, *, limit: int, before: datetime | None) -> list[dict]:
        return []


class MongoMessageStore:
    enabled = True

    def __init__(self, db: AsyncDatabase) -> None:
        self._collection = db.chat_messages

    async def save(self, event: dict, user_id: ObjectId) -> None:
        await self._collection.insert_one({
            "_id": event["id"],
            "room_id": event["room"],
            "user_id": user_id,
            "user_name": event["user"]["name"],
            "text": event["text"],
            "sent_at": datetime.fromisoformat(event["sent_at"]),
        })

    async def history(self, room_id: str, *, limit: int, before: datetime | None) -> list[dict]:
        flt: dict = {"room_id": room_id}
        if before is not None:
            flt["sent_at"] = {"$lt": before}
        cursor = self._collection.find(flt).sort("sent_at", -1).limit(limit)
        docs = [d async for d in cursor]
        docs.reverse()  # ordem cronológica
        return [
            {
                "type": "message",
                "id": d["_id"],
                "room": d["room_id"],
                "user": {"id": str(d["user_id"]) if d.get("user_id") else None, "name": d["user_name"]},
                "text": d["text"],
                "sent_at": d["sent_at"].isoformat(),
            }
            for d in docs
        ]


def build_store(enabled: bool, db: AsyncDatabase):
    return MongoMessageStore(db) if enabled else NullMessageStore()
