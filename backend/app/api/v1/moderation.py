from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import Db, ModeratorUser, Paging
from app.core.errors import NotFound
from app.models.common import ModerationStatus, Page, RejectRequest
from app.models.curiosity import CuriosityOut
from app.models.landmark import LandmarkOut
from app.repositories import curiosities as curiosities_repo
from app.repositories import landmarks as landmarks_repo
from app.repositories.common import parse_object_id

router = APIRouter(prefix="/moderation", tags=["Moderação"])

QueueStatus = Annotated[
    ModerationStatus, Query(alias="status", description="Fila a listar (padrão: pendentes).")
]


@router.get("/landmarks", response_model=Page[LandmarkOut], summary="Fila de pontos sugeridos")
async def landmark_queue(_: ModeratorUser, db: Db, paging: Paging,
                         status_: QueueStatus = ModerationStatus.PENDING):
    items, total = await landmarks_repo.list_page(
        db, {"status": status_.value}, page=paging.page, page_size=paging.page_size,
        newest_first=status_ != ModerationStatus.PENDING,
    )
    return Page(items=[landmarks_repo.to_out(d) for d in items], total=total,
                page=paging.page, page_size=paging.page_size)


@router.post("/landmarks/{landmark_id}/approve", response_model=LandmarkOut, summary="Aprovar ponto")
async def approve_landmark(landmark_id: str, moderator: ModeratorUser, db: Db):
    return await _set_landmark(db, landmark_id, moderator, ModerationStatus.APPROVED)


@router.post("/landmarks/{landmark_id}/reject", response_model=LandmarkOut, summary="Rejeitar ponto")
async def reject_landmark(landmark_id: str, body: RejectRequest, moderator: ModeratorUser, db: Db):
    return await _set_landmark(db, landmark_id, moderator, ModerationStatus.REJECTED, body.reason)


@router.get("/curiosities", response_model=Page[CuriosityOut], summary="Fila de curiosidades")
async def curiosity_queue(_: ModeratorUser, db: Db, paging: Paging,
                          status_: QueueStatus = ModerationStatus.PENDING):
    items, total = await curiosities_repo.list_page(
        db, {"status": status_.value}, page=paging.page, page_size=paging.page_size,
        newest_first=status_ != ModerationStatus.PENDING,
    )
    return Page(items=[curiosities_repo.to_out(d) for d in items], total=total,
                page=paging.page, page_size=paging.page_size)


@router.post("/curiosities/{curiosity_id}/approve", response_model=CuriosityOut, summary="Aprovar curiosidade")
async def approve_curiosity(curiosity_id: str, moderator: ModeratorUser, db: Db):
    return await _set_curiosity(db, curiosity_id, moderator, ModerationStatus.APPROVED)


@router.post("/curiosities/{curiosity_id}/reject", response_model=CuriosityOut, summary="Rejeitar curiosidade")
async def reject_curiosity(curiosity_id: str, body: RejectRequest, moderator: ModeratorUser, db: Db):
    return await _set_curiosity(db, curiosity_id, moderator, ModerationStatus.REJECTED, body.reason)


async def _set_landmark(db, landmark_id: str, moderator: dict, status_: ModerationStatus, reason=None):
    lid = parse_object_id(landmark_id, "Ponto histórico")
    doc = await landmarks_repo.set_status(db, lid, status_, moderator_id=moderator["_id"], reason=reason)
    if doc is None:
        raise NotFound("Ponto histórico não encontrado.")
    return landmarks_repo.to_out(await landmarks_repo.get(db, lid, with_count=True))


async def _set_curiosity(db, curiosity_id: str, moderator: dict, status_: ModerationStatus, reason=None):
    cid = parse_object_id(curiosity_id, "Curiosidade")
    doc = await curiosities_repo.set_status(db, cid, status_, moderator_id=moderator["_id"], reason=reason)
    if doc is None:
        raise NotFound("Curiosidade não encontrada.")
    return curiosities_repo.to_out(doc)
