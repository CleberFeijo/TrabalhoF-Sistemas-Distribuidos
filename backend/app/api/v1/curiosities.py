from fastapi import APIRouter, status

from app.api.deps import CurrentUser, Db, is_moderator
from app.core.errors import Forbidden, NotFound
from app.models.common import ModerationStatus
from app.models.curiosity import CuriosityOut
from app.repositories import curiosities as curiosities_repo
from app.repositories.common import parse_object_id

router = APIRouter(prefix="/curiosities", tags=["Curiosidades"])


async def _get_visible(db, curiosity_id: str, user: dict) -> dict:
    doc = await curiosities_repo.get(db, parse_object_id(curiosity_id, "Curiosidade"))
    if doc is None:
        raise NotFound("Curiosidade não encontrada.")
    is_author = doc.get("author_id") == user["_id"]
    if doc["status"] != ModerationStatus.APPROVED.value and not (is_author or is_moderator(user)):
        raise NotFound("Curiosidade não encontrada.")
    return doc


@router.get("/{curiosity_id}", response_model=CuriosityOut, summary="Detalhar curiosidade")
async def get_curiosity(curiosity_id: str, user: CurrentUser, db: Db):
    return curiosities_repo.to_out(await _get_visible(db, curiosity_id, user))


@router.delete(
    "/{curiosity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir curiosidade",
    description="Permitido ao autor e a moderadores.",
)
async def delete_curiosity(curiosity_id: str, user: CurrentUser, db: Db):
    doc = await _get_visible(db, curiosity_id, user)
    if doc.get("author_id") != user["_id"] and not is_moderator(user):
        raise Forbidden()
    await curiosities_repo.delete(db, doc["_id"])
