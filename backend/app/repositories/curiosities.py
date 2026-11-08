from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.models.common import ModerationStatus
from app.repositories.common import author_lookup_stages, user_summary, utcnow

_LANDMARK_NAME_STAGES = [
    {
        "$lookup": {
            "from": "landmarks",
            "localField": "landmark_id",
            "foreignField": "_id",
            "pipeline": [{"$project": {"name": 1}}],
            "as": "_lm",
        }
    },
    {"$set": {"landmark_name": {"$first": "$_lm.name"}}},
    {"$unset": "_lm"},
]


def to_out(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "landmark_id": str(doc["landmark_id"]),
        "landmark_name": doc.get("landmark_name"),
        "text": doc["text"],
        "author": user_summary(doc.get("author")),
        "source": doc.get("source"),
        "status": doc["status"],
        "rejection_reason": doc.get("rejection_reason"),
        "created_at": doc["created_at"],
    }


async def create(
    db: AsyncDatabase, *, landmark_id: ObjectId, text: str,
    author_id: ObjectId | None, status: ModerationStatus, source: dict | None = None,
) -> dict:
    now = utcnow()
    doc = {
        "landmark_id": landmark_id,
        "text": text,
        "author_id": author_id,
        "source": source,
        "status": status.value,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.curiosities.insert_one(doc)
    return await get(db, result.inserted_id)


async def get(db: AsyncDatabase, curiosity_id: ObjectId) -> dict | None:
    pipeline = [{"$match": {"_id": curiosity_id}}, *author_lookup_stages(), *_LANDMARK_NAME_STAGES]
    docs = await (await db.curiosities.aggregate(pipeline)).to_list()
    return docs[0] if docs else None


async def list_page(
    db: AsyncDatabase, flt: dict, *, page: int, page_size: int, newest_first: bool = True,
):
    total = await db.curiosities.count_documents(flt)
    pipeline = [
        {"$match": flt},
        {"$sort": {"created_at": -1 if newest_first else 1, "_id": -1 if newest_first else 1}},
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size},
        *author_lookup_stages(),
        *_LANDMARK_NAME_STAGES,
    ]
    return await (await db.curiosities.aggregate(pipeline)).to_list(), total


async def set_status(
    db: AsyncDatabase, curiosity_id: ObjectId, status: ModerationStatus, *,
    moderator_id: ObjectId, reason: str | None = None,
) -> dict | None:
    now = utcnow()
    updated = await db.curiosities.find_one_and_update(
        {"_id": curiosity_id},
        {"$set": {
            "status": status.value,
            "rejection_reason": reason,
            "moderated_by": moderator_id,
            "moderated_at": now,
            "updated_at": now,
        }},
        return_document=ReturnDocument.AFTER,
    )
    return await get(db, curiosity_id) if updated else None


async def delete(db: AsyncDatabase, curiosity_id: ObjectId) -> bool:
    result = await db.curiosities.delete_one({"_id": curiosity_id})
    return result.deleted_count == 1
