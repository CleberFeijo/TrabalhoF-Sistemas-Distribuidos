from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, Db, ModeratorUser, Paging, has_role, is_moderator
from app.core.config import get_settings
from app.core.errors import Forbidden, NotFound
from app.models.common import ModerationStatus, Page
from app.models.curiosity import CuriosityCreate, CuriosityOut
from app.models.landmark import LandmarkCreate, LandmarkOut, LandmarkUpdate, NearbyLandmark
from app.models.user import Role
from app.repositories import curiosities as curiosities_repo
from app.repositories import landmarks as landmarks_repo
from app.repositories.common import parse_object_id

router = APIRouter(prefix="/landmarks", tags=["Pontos históricos"])

APPROVED = ModerationStatus.APPROVED.value


def _can_see(landmark: dict, user: dict) -> bool:
    return (
        landmark["status"] == APPROVED
        or landmark.get("created_by") == user["_id"]
        or is_moderator(user)
    )


async def _get_visible(db, landmark_id: str, user: dict) -> dict:
    landmark = await landmarks_repo.get(db, parse_object_id(landmark_id, "Ponto histórico"), with_count=True)
    if landmark is None or not _can_see(landmark, user):
        raise NotFound("Ponto histórico não encontrado.")
    return landmark


@router.get(
    "/nearby",
    response_model=list[NearbyLandmark],
    summary="Pontos históricos próximos",
    description="Pontos aprovados dentro do raio, do mais próximo para o mais distante.",
)
async def nearby(
    user: CurrentUser,
    db: Db,
    lat: Annotated[float, Query(ge=-90, le=90, description="Latitude do usuário.")],
    lon: Annotated[float, Query(ge=-180, le=180, description="Longitude do usuário.")],
    radius: Annotated[int | None, Query(ge=1, description="Raio em metros (padrão 200).")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    settings = get_settings()
    radius_m = min(radius or settings.NEARBY_DEFAULT_RADIUS_M, settings.NEARBY_MAX_RADIUS_M)
    docs = await landmarks_repo.nearby(
        db, latitude=lat, longitude=lon, radius_m=radius_m, limit=min(limit, settings.NEARBY_MAX_RESULTS)
    )
    return [
        NearbyLandmark(
            **landmarks_repo.to_out(d),
            distance_m=round(d["distance_m"], 1),
            chat_available=d["distance_m"] <= settings.CHAT_JOIN_RADIUS_M,
        )
        for d in docs
    ]


@router.post(
    "",
    response_model=LandmarkOut,
    status_code=status.HTTP_201_CREATED,
    summary="Sugerir ponto histórico",
    description="Usuários comuns criam como `pending`; moderadores e admins publicam direto.",
)
async def create_landmark(body: LandmarkCreate, user: CurrentUser, db: Db):
    status_ = ModerationStatus.APPROVED if is_moderator(user) else ModerationStatus.PENDING
    data = body.model_dump(exclude={"curiosity"})
    landmark = await landmarks_repo.create(db, data, created_by=user["_id"], status=status_)
    count = 0
    if body.curiosity:
        await curiosities_repo.create(
            db, landmark_id=landmark["_id"], text=body.curiosity, author_id=user["_id"], status=status_
        )
        count = 1 if status_ == ModerationStatus.APPROVED else 0
    return LandmarkOut(**{**landmarks_repo.to_out(landmark), "curiosity_count": count})


@router.get("/{landmark_id}", response_model=LandmarkOut, summary="Detalhar ponto histórico")
async def get_landmark(landmark_id: str, user: CurrentUser, db: Db):
    return landmarks_repo.to_out(await _get_visible(db, landmark_id, user))


@router.patch("/{landmark_id}", response_model=LandmarkOut, summary="Editar ponto (moderador)")
async def update_landmark(landmark_id: str, body: LandmarkUpdate, _: ModeratorUser, db: Db):
    lid = parse_object_id(landmark_id, "Ponto histórico")
    fields = body.model_dump(exclude_unset=True)
    # Campos obrigatórios não podem ser apagados com null.
    for required in ("name", "latitude", "longitude"):
        if required in fields and fields[required] is None:
            fields.pop(required)
    if not fields:
        landmark = await landmarks_repo.get(db, lid, with_count=True)
    else:
        landmark = await landmarks_repo.update(db, lid, fields)
        landmark = landmark and await landmarks_repo.get(db, lid, with_count=True)
    if landmark is None:
        raise NotFound("Ponto histórico não encontrado.")
    return landmarks_repo.to_out(landmark)


@router.delete(
    "/{landmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir ponto",
    description="Admins excluem qualquer ponto; o autor pode excluir a própria sugestão ainda não aprovada. "
    "Remove também as curiosidades do ponto.",
)
async def delete_landmark(landmark_id: str, user: CurrentUser, db: Db):
    landmark = await _get_visible(db, landmark_id, user)
    own_unpublished = landmark.get("created_by") == user["_id"] and landmark["status"] != APPROVED
    if not (has_role(user, Role.ADMIN) or own_unpublished):
        raise Forbidden()
    await landmarks_repo.delete(db, landmark["_id"])


@router.get(
    "/{landmark_id}/curiosities",
    response_model=Page[CuriosityOut],
    summary="Curiosidades aprovadas do ponto",
)
async def list_curiosities(landmark_id: str, user: CurrentUser, db: Db, paging: Paging):
    landmark = await _get_visible(db, landmark_id, user)
    items, total = await curiosities_repo.list_page(
        db, {"landmark_id": landmark["_id"], "status": APPROVED},
        page=paging.page, page_size=paging.page_size,
    )
    return Page(items=[curiosities_repo.to_out(d) for d in items], total=total,
                page=paging.page, page_size=paging.page_size)


@router.post(
    "/{landmark_id}/curiosities",
    response_model=CuriosityOut,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar curiosidade",
    description="Entra como `pending` até um moderador aprovar (moderadores publicam direto). "
    "O autor é sempre o usuário do token.",
)
async def create_curiosity(landmark_id: str, body: CuriosityCreate, user: CurrentUser, db: Db):
    landmark = await _get_visible(db, landmark_id, user)
    status_ = ModerationStatus.APPROVED if is_moderator(user) else ModerationStatus.PENDING
    doc = await curiosities_repo.create(
        db, landmark_id=landmark["_id"], text=body.text, author_id=user["_id"], status=status_
    )
    return curiosities_repo.to_out(doc)
