from __future__ import annotations

from datetime import datetime, timedelta
from jose import jwt

from core.config import settings
from core.security import verify_password
from app.crud.crud_user import CRUDUser
from utils.fastapi.schemas.users import UserCreateSchema, UserLogSchema
from core.security import OAuth2CustomBearer
from fastapi.security import OAuth2PasswordRequestForm

oauth2_scheme = OAuth2CustomBearer(
    password_token_url=f"/auth/login",
    client_credentials_token_url=f"/auth/token",
)


def authenticate(user: OAuth2PasswordRequestForm):
    user_obj = CRUDUser()
    user_db = user_obj.get_by_email(user.username)

    if not user_db:
        return None
    if not verify_password(user.password, user_db.get("hashed_password")):
        return None
    return user_db


def create_access_token(*, sub: str) -> str:  # 2
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(minutes=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES),  # 3
        sub=sub,
    )


def _create_token(
    token_type: str,
    lifetime: timedelta,
    sub: str,
) -> str:
    crud_obj = CRUDUser()

    iat = datetime.utcnow()
    expire = iat + lifetime
    payload = {
        "type": token_type,
        "exp": expire,  # 4
        "iat": iat,  # 5
        "sub": str(sub),  # 6
    }

    crud_obj.logged(UserLogSchema(user_id=sub, logged=True))

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
