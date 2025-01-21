from fastapi import APIRouter, Depends
from utils.fastapi.schemas import auth, users
from fastapi.security import OAuth2PasswordRequestForm
from core.auth import authenticate, create_access_token
from core.config import settings
from ..deps import get_current_user
from app.crud.crud_user import CRUDUser

router = APIRouter(prefix='/auth', tags=["Autenticação"])


@router.post(
    "/login",
    summary="Autenticação de Usuário",
    response_model=auth.ResponseToken
)
def login_user_auth(login: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(login)
    if not user:
        raise Exception("Incorrect username or password")
    return auth.ResponseToken(
        access_token=create_access_token(sub=str(user.get("_id"))),
        expires_in=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@router.post(
    "/logout",
    summary="Desconectar",
    description="Retira a sessão e o acesso do usuário, até novo login ser efetuado!",
)
def logout(user=Depends(get_current_user)):
    CRUDUser(user).logged(users.UserLogSchema(user_id=user.id, logged=False))
    return {"message": "Usuário desconectado com sucesso!"}
