from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.models.common import ModerationStatus
from app.repositories.common import geo_point, utcnow

APPROVED = ModerationStatus.APPROVED.value

# Conta as curiosidades aprovadas de cada ponto.
_COUNT_STAGES = [
    {
        "$lookup": {
            "from": "curiosities",
            "localField": "_id",
            "foreignField": "landmark_id",
            "pipeline": [{"$match": {"status": APPROVED}}, {"$count": "n"}],
            "as": "_cc",
        }
    },
    {"$set": {"curiosity_count": {"$ifNull": [{"$first": "$_cc.n"}, 0]}}},
    {"$unset": "_cc"},
]


def to_out(doc: dict) -> dict:
    lon, lat = doc["location"]["coordinates"]
    created_by = doc.get("created_by")
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "description": doc.get("description"),
        "latitude": lat,
        "longitude": lon,
        "category": doc.get("category"),
        "address": doc.get("address"),
        "city": doc.get("city"),
        "state": doc.get("state"),
        "country": doc.get("country"),
        "image_url": doc.get("image_url"),
        "source": doc.get("source"),
        "status": doc["status"],
        "rejection_reason": doc.get("rejection_reason"),
        "created_by": str(created_by) if created_by else None,
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
        "curiosity_count": doc.get("curiosity_count", 0),
    }


async def create(db: AsyncDatabase, data: dict, *, created_by: ObjectId | None, status: ModerationStatus) -> dict:
    now = utcnow()
    doc = {
        "name": data["name"],
        "description": data.get("description"),
        "location": geo_point(data["latitude"], data["longitude"]),
        "category": data.get("category"),
        "address": data.get("address"),
        "city": data.get("city"),
        "state": data.get("state"),
        "country": data.get("country", "BR"),
        "image_url": str(data["image_url"]) if data.get("image_url") else None,
        "source": data.get("source"),
        "status": status.value,
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.landmarks.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def get(db: AsyncDatabase, landmark_id: ObjectId, *, with_count: bool = False) -> dict | None:
    if not with_count:
        return await db.landmarks.find_one({"_id": landmark_id})
    docs = await (await db.landmarks.aggregate([{"$match": {"_id": landmark_id}}, *_COUNT_STAGES])).to_list()
    return docs[0] if docs else None


async def nearby(db: AsyncDatabase, *, latitude: float, longitude: float, radius_m: float, limit: int) -> list[dict]:
    pipeline = [
        {
            "$geoNear": {
                "near": geo_point(latitude, longitude),
                "distanceField": "distance_m",
                "maxDistance": radius_m,
                "spherical": True,
                "query": {"status": APPROVED},
                "key": "location",
            }
        },
        {"$limit": limit},
        *_COUNT_STAGES,
    ]
    return await (await db.landmarks.aggregate(pipeline)).to_list()


async def list_page(db: AsyncDatabase, flt: dict, *, page: int, page_size: int, newest_first: bool = True):
    total = await db.landmarks.count_documents(flt)
    pipeline = [
        {"$match": flt},
        {"$sort": {"created_at": -1 if newest_first else 1, "_id": -1 if newest_first else 1}},
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size},
        *_COUNT_STAGES,
    ]
    return await (await db.landmarks.aggregate(pipeline)).to_list(), total


async def update(db: AsyncDatabase, landmark_id: ObjectId, data: dict) -> dict | None:
    fields = {k: v for k, v in data.items() if k not in ("latitude", "longitude")}
    if "image_url" in fields and fields["image_url"] is not None:
        fields["image_url"] = str(fields["image_url"])
    if "latitude" in data or "longitude" in data:
        current = await db.landmarks.find_one({"_id": landmark_id}, {"location": 1})
        if current is None:
            return None
        lon, lat = current["location"]["coordinates"]
        fields["location"] = geo_point(data.get("latitude", lat), data.get("longitude", lon))
    fields["updated_at"] = utcnow()
    return await db.landmarks.find_one_and_update(
        {"_id": landmark_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
    )


async def set_status(
    db: AsyncDatabase, landmark_id: ObjectId, status: ModerationStatus, *,
    moderator_id: ObjectId, reason: str | None = None,
) -> dict | None:
    now = utcnow()
    return await db.landmarks.find_one_and_update(
        {"_id": landmark_id},
        {"$set": {
            "status": status.value,
            "rejection_reason": reason,
            "moderated_by": moderator_id,
            "moderated_at": now,
            "updated_at": now,
        }},
        return_document=ReturnDocument.AFTER,
    )


async def delete(db: AsyncDatabase, landmark_id: ObjectId) -> bool:
    result = await db.landmarks.delete_one({"_id": landmark_id})
    if result.deleted_count:
        await db.curiosities.delete_many({"landmark_id": landmark_id})
        await db.chat_messages.delete_many({"room_id": str(landmark_id)})
    return result.deleted_count == 1
