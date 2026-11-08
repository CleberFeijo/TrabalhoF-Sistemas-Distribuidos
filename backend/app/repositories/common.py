from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId

from app.core.errors import NotFound


def utcnow() -> datetime:
    return datetime.now(UTC)


def parse_object_id(value: str, what: str = "Recurso") -> ObjectId:
    """Converte um id da URL; ids malformados viram 404 (não 500)."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise NotFound(f"{what} não encontrado.") from None


def geo_point(latitude: float, longitude: float) -> dict:
    # GeoJSON usa a ordem [longitude, latitude].
    return {"type": "Point", "coordinates": [longitude, latitude]}


def author_lookup_stages(field: str = "author_id", as_: str = "author") -> list[dict]:
    """Estágios de agregação que resolvem o autor (nome atual) a partir do id."""
    return [
        {
            "$lookup": {
                "from": "users",
                "localField": field,
                "foreignField": "_id",
                "pipeline": [{"$project": {"name": 1, "last_name": 1}}],
                "as": f"_{as_}",
            }
        },
        {"$set": {as_: {"$first": f"$_{as_}"}}},
        {"$unset": f"_{as_}"},
    ]


def user_summary(doc: dict | None) -> dict | None:
    if not doc:
        return None
    return {"id": str(doc["_id"]), "name": f"{doc['name']} {doc['last_name']}".strip()}
