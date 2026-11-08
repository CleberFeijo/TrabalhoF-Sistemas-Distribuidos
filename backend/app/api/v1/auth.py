from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, Db
from app.core.errors import Unauthorized
from app.core.security import burn_password_check, create_access_token, verify_password
from app.models.common import Message
from app.models.user import RegisterRequest, TokenResponse
from app.repositories import users as users_repo

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _token_response(user: dict) -> TokenResponse:
    token, expires_in = create_access_token(str(user["_id"]), user.get("token_version", 0))
    return TokenResponse(access_token=token, expires_in=expires_in, user=users_repo.to_out(user))


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro público de usuário",
    description="Cria uma conta com papel `user` e já devolve um token de acesso.",
)
async def register(body: RegisterRequest, db: Db):
    user = await users_repo.create(
        db, name=body.name, last_name=body.last_name, email=body.email, password=body.password
    )
    return _token_response(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login (OAuth2 password flow)",
    description="Envie `username` (email) e `password` como `application/x-www-form-urlencoded`.",
)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Db):
    user = await users_repo.get_by_email(db, form.username.strip())
    if user is None:
        burn_password_check(form.password)
        raise Unauthorized("Email ou senha incorretos.", code="invalid_credentials")
    if not verify_password(form.password, user.get("password_hash")):
        raise Unauthorized("Email ou senha incorretos.", code="invalid_credentials")
    if not user.get("is_active", True):
        raise Unauthorized("Conta desativada.", code="account_disabled")
    return _token_response(user)


@router.post(
    "/logout",
    response_model=Message,
    summary="Encerrar sessões",
    description="Invalida todos os tokens do usuário (todos os dispositivos).",
)
async def logout(user: CurrentUser, db: Db):
    await users_repo.bump_token_version(db, user["_id"])
    return Message(message="Sessão encerrada.")
