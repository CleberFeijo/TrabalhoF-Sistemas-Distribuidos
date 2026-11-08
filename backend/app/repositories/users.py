import re

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.errors import Conflict
from app.core.security import hash_password
from app.models.common import ModerationStatus
from app.models.user import Plan, Role
from app.repositories.common import utcnow


def to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "last_name": doc["last_name"],
        "email": doc["email"],
        "roles": doc.get("roles", [Role.USER.value]),
        "plan": doc.get("plan", Plan.FREE.value),
        "is_active": doc.get("is_active", True),
        "created_at": doc["created_at"],
    }


async def create(
    db: AsyncDatabase,
    *,
    name: str,
    last_name: str,
    email: str,
    password: str,
    roles: list[Role] | None = None,
) -> dict:
    now = utcnow()
    doc = {
        "name": name,
        "last_name": last_name,
        "email": email.lower(),
        "password_hash": hash_password(password),
        "roles": [r.value for r in (roles or [Role.USER])],
        "plan": Plan.FREE.value,
        "is_active": True,
        "token_version": 0,
        "created_at": now,
        "updated_at": now,
    }
    try:
        result = await db.users.insert_one(doc)
    except DuplicateKeyError:
        raise Conflict("Este email já está cadastrado.", code="email_taken") from None
    doc["_id"] = result.inserted_id
    return doc


async def get_by_id(db: AsyncDatabase, user_id: ObjectId) -> dict | None:
    return await db.users.find_one({"_id": user_id})


async def get_by_email(db: AsyncDatabase, email: str) -> dict | None:
    return await db.users.find_one({"email": email.lower()})


async def update(db: AsyncDatabase, user_id: ObjectId, fields: dict) -> dict | None:
    fields = {**fields, "updated_at": utcnow()}
    try:
        return await db.users.find_one_and_update(
            {"_id": user_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        raise Conflict("Este email já está cadastrado.", code="email_taken") from None


async def bump_token_version(db: AsyncDatabase, user_id: ObjectId, extra: dict | None = None) -> dict:
    """Invalida todos os tokens emitidos até agora para o usuário."""
    return await db.users.find_one_and_update(
        {"_id": user_id},
        {"$inc": {"token_version": 1}, "$set": {"updated_at": utcnow(), **(extra or {})}},
        return_document=ReturnDocument.AFTER,
    )


async def list_page(db: AsyncDatabase, *, query: str | None, page: int, page_size: int):
    flt: dict = {}
    if query:
        rx = {"$regex": re.escape(query), "$options": "i"}
        flt = {"$or": [{"name": rx}, {"last_name": rx}, {"email": rx}]}
    total = await db.users.count_documents(flt)
    cursor = db.users.find(flt).sort("created_at", -1).skip((page - 1) * page_size).limit(page_size)
    return [doc async for doc in cursor], total


async def count_admins(db: AsyncDatabase, *, exclude: ObjectId | None = None) -> int:
    flt: dict = {"roles": Role.ADMIN.value, "is_active": True}
    if exclude is not None:
        flt["_id"] = {"$ne": exclude}
    return await db.users.count_documents(flt)


async def delete(db: AsyncDatabase, user_id: ObjectId) -> bool:
    """Exclui a conta.

    Conteúdo aprovado permanece publicado de forma anônima (autor nulo);
    conteúdo pendente ou rejeitado é apagado junto com a conta.
    """
    not_approved = {"$ne": ModerationStatus.APPROVED.value}
    landmarks_to_drop = [
        d["_id"]
        async for d in db.landmarks.find({"created_by": user_id, "status": not_approved}, {"_id": 1})
    ]
    if landmarks_to_drop:
        await db.curiosities.delete_many({"landmark_id": {"$in": landmarks_to_drop}})
        await db.landmarks.delete_many({"_id": {"$in": landmarks_to_drop}})
    await db.curiosities.delete_many({"author_id": user_id, "status": not_approved})
    await db.curiosities.update_many({"author_id": user_id}, {"$set": {"author_id": None}})
    await db.landmarks.update_many({"created_by": user_id}, {"$set": {"created_by": None}})
    await db.chat_messages.delete_many({"user_id": user_id})
    result = await db.users.delete_one({"_id": user_id})
    return result.deleted_count == 1
