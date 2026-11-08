from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.core.errors import Forbidden, Unauthorized
from app.core.security import decode_access_token
from app.db.mongo import get_database
from app.models.user import Role
from app.repositories import users as users_repo
from app.repositories.common import parse_object_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)

Db = Annotated[AsyncDatabase, Depends(get_database)]


async def resolve_user_from_token(db: AsyncDatabase, token: str | None) -> dict:
    """Valida o token e devolve o usuário; usado pelas rotas HTTP e pelo WebSocket."""
    if not token:
        raise Unauthorized("Token de acesso ausente.")
    payload = decode_access_token(token)
    if payload is None:
        raise Unauthorized("Token inválido ou expirado.")
    try:
        user_id = parse_object_id(payload["sub"])
    except Exception:
        raise Unauthorized("Token inválido ou expirado.") from None
    user = await users_repo.get_by_id(db, user_id)
    if user is None or not user.get("is_active", True):
        raise Unauthorized("Token inválido ou expirado.")
    if payload["ver"] != user.get("token_version", 0):
        raise Unauthorized("Sessão encerrada. Faça login novamente.", code="session_revoked")
    return user


async def get_current_user(db: Db, token: Annotated[str | None, Depends(oauth2_scheme)]) -> dict:
    return await resolve_user_from_token(db, token)


CurrentUser = Annotated[dict, Depends(get_current_user)]


def has_role(user: dict, *roles: Role) -> bool:
    user_roles = set(user.get("roles", []))
    return Role.ADMIN.value in user_roles or any(r.value in user_roles for r in roles)


def is_moderator(user: dict) -> bool:
    return has_role(user, Role.MODERATOR)


def require_roles(*roles: Role):
    async def checker(user: CurrentUser) -> dict:
        if not has_role(user, *roles):
            raise Forbidden()
        return user

    return checker


ModeratorUser = Annotated[dict, Depends(require_roles(Role.MODERATOR))]
AdminUser = Annotated[dict, Depends(require_roles(Role.ADMIN))]


class Pagination:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Página (começa em 1).")] = 1,
        page_size: Annotated[int, Query(ge=1, le=100, description="Itens por página.")] = 20,
    ):
        self.page = page
        self.page_size = page_size


Paging = Annotated[Pagination, Depends()]
