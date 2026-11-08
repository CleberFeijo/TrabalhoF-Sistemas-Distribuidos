from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import AdminUser, CurrentUser, Db, Paging
from app.core.errors import Conflict, Forbidden, NotFound, Unauthorized
from app.core.security import create_access_token, hash_password, verify_password
from app.models.common import ModerationStatus, Page
from app.models.curiosity import CuriosityOut
from app.models.landmark import LandmarkOut
from app.models.user import (
    AdminUserUpdate,
    ChangePasswordRequest,
    DeleteAccountRequest,
    Role,
    TokenResponse,
    UpdateMeRequest,
    UserOut,
)
from app.repositories import curiosities as curiosities_repo
from app.repositories import landmarks as landmarks_repo
from app.repositories import users as users_repo
from app.repositories.common import parse_object_id

router = APIRouter(prefix="/users", tags=["Usuários"])

StatusFilter = Annotated[ModerationStatus | None, Query(alias="status", description="Filtra por status de moderação.")]


# ------------------------------------------------------------------ conta própria

@router.get("/me", response_model=UserOut, summary="Perfil do usuário logado")
async def get_me(user: CurrentUser):
    return users_repo.to_out(user)


@router.patch("/me", response_model=UserOut, summary="Atualizar o próprio perfil")
async def update_me(body: UpdateMeRequest, user: CurrentUser, db: Db):
    fields = body.model_dump(exclude_unset=True, exclude={"current_password"}, exclude_none=True)
    if "email" in fields and fields["email"] != user["email"]:
        if not body.current_password or not verify_password(body.current_password, user.get("password_hash")):
            raise Unauthorized("Senha atual incorreta.", code="invalid_password")
    else:
        fields.pop("email", None)
    if not fields:
        return users_repo.to_out(user)
    updated = await users_repo.update(db, user["_id"], fields)
    return users_repo.to_out(updated)


@router.post("/me/password", summary="Trocar a própria senha", response_model=TokenResponse,
             description="Encerra todas as sessões e devolve um token novo para este dispositivo.")
async def change_password(body: ChangePasswordRequest, user: CurrentUser, db: Db):
    if not verify_password(body.current_password, user.get("password_hash")):
        raise Unauthorized("Senha atual incorreta.", code="invalid_password")
    updated = await users_repo.bump_token_version(
        db, user["_id"], {"password_hash": hash_password(body.new_password)}
    )
    token, expires_in = create_access_token(str(updated["_id"]), updated["token_version"])
    return TokenResponse(access_token=token, expires_in=expires_in, user=users_repo.to_out(updated))


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir a própria conta",
    description=(
        "Exige a senha. Curiosidades e pontos já aprovados continuam publicados sem autoria; "
        "conteúdo pendente ou rejeitado é apagado."
    ),
)
async def delete_me(body: DeleteAccountRequest, user: CurrentUser, db: Db):
    if not verify_password(body.password, user.get("password_hash")):
        raise Unauthorized("Senha incorreta.", code="invalid_password")
    if Role.ADMIN.value in user.get("roles", []) and await users_repo.count_admins(db, exclude=user["_id"]) == 0:
        raise Conflict("Você é o único administrador; promova outro antes de excluir a conta.")
    await users_repo.delete(db, user["_id"])


@router.get("/me/curiosities", response_model=Page[CuriosityOut], summary="Minhas curiosidades")
async def my_curiosities(user: CurrentUser, db: Db, paging: Paging, status_: StatusFilter = None):
    flt: dict = {"author_id": user["_id"]}
    if status_:
        flt["status"] = status_.value
    items, total = await curiosities_repo.list_page(db, flt, page=paging.page, page_size=paging.page_size)
    return Page(items=[curiosities_repo.to_out(d) for d in items], total=total,
                page=paging.page, page_size=paging.page_size)


@router.get("/me/landmarks", response_model=Page[LandmarkOut], summary="Pontos que sugeri")
async def my_landmarks(user: CurrentUser, db: Db, paging: Paging, status_: StatusFilter = None):
    flt: dict = {"created_by": user["_id"]}
    if status_:
        flt["status"] = status_.value
    items, total = await landmarks_repo.list_page(db, flt, page=paging.page, page_size=paging.page_size)
    return Page(items=[landmarks_repo.to_out(d) for d in items], total=total,
                page=paging.page, page_size=paging.page_size)


# ------------------------------------------------------------------ administração

@router.get("", response_model=Page[UserOut], summary="Listar usuários (admin)")
async def list_users(_: AdminUser, db: Db, paging: Paging,
                     q: Annotated[str | None, Query(max_length=100, description="Busca por nome ou email.")] = None):
    items, total = await users_repo.list_page(db, query=q, page=paging.page, page_size=paging.page_size)
    return Page(items=[users_repo.to_out(d) for d in items], total=total,
                page=paging.page, page_size=paging.page_size)


@router.get("/{user_id}", response_model=UserOut, summary="Detalhar usuário (admin)")
async def get_user(user_id: str, _: AdminUser, db: Db):
    user = await users_repo.get_by_id(db, parse_object_id(user_id, "Usuário"))
    if user is None:
        raise NotFound("Usuário não encontrado.")
    return users_repo.to_out(user)


@router.patch("/{user_id}", response_model=UserOut, summary="Alterar papéis, plano ou status (admin)")
async def admin_update_user(user_id: str, body: AdminUserUpdate, admin: AdminUser, db: Db):
    target_id = parse_object_id(user_id, "Usuário")
    target = await users_repo.get_by_id(db, target_id)
    if target is None:
        raise NotFound("Usuário não encontrado.")

    fields = body.model_dump(exclude_unset=True, exclude_none=True)
    if "roles" in fields:
        roles = {Role(r) for r in fields["roles"]} | {Role.USER}
        fields["roles"] = sorted(r.value for r in roles)
    if "plan" in fields:
        fields["plan"] = fields["plan"].value if hasattr(fields["plan"], "value") else fields["plan"]

    losing_admin = Role.ADMIN.value in target.get("roles", []) and (
        ("roles" in fields and Role.ADMIN.value not in fields["roles"])
        or fields.get("is_active") is False
    )
    if losing_admin and await users_repo.count_admins(db, exclude=target_id) == 0:
        raise Conflict("Não é possível remover o último administrador ativo.")
    if target_id == admin["_id"] and fields.get("is_active") is False:
        raise Forbidden("Você não pode desativar a própria conta.")

    if not fields:
        return users_repo.to_out(target)
    # Mudança de papel ou desativação encerra as sessões do usuário afetado.
    if "roles" in fields or "is_active" in fields:
        updated = await users_repo.bump_token_version(db, target_id, fields)
    else:
        updated = await users_repo.update(db, target_id, fields)
    return users_repo.to_out(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir usuário (admin)")
async def admin_delete_user(user_id: str, admin: AdminUser, db: Db):
    target_id = parse_object_id(user_id, "Usuário")
    if target_id == admin["_id"]:
        raise Forbidden("Use DELETE /users/me para excluir a própria conta.")
    target = await users_repo.get_by_id(db, target_id)
    if target is None:
        raise NotFound("Usuário não encontrado.")
    if Role.ADMIN.value in target.get("roles", []) and await users_repo.count_admins(db, exclude=target_id) == 0:
        raise Conflict("Não é possível excluir o último administrador ativo.")
    await users_repo.delete(db, target_id)
