from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field, field_validator

from app.core.security import BCRYPT_MAX_BYTES
from app.models.common import ApiModel


class Role(StrEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class Plan(StrEnum):
    FREE = "free"
    PREMIUM = "premium"


def _check_password(value: str) -> str:
    if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError(f"A senha pode ter no máximo {BCRYPT_MAX_BYTES} bytes.")
    return value


PasswordStr = Annotated[
    str, Field(min_length=8, max_length=BCRYPT_MAX_BYTES), AfterValidator(_check_password)
]
NameStr = Annotated[str, Field(min_length=1, max_length=60)]


class RegisterRequest(ApiModel):
    name: NameStr
    last_name: NameStr
    email: EmailStr
    password: PasswordStr

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()


class UserOut(BaseModel):
    id: str
    name: str
    last_name: str
    email: str
    roles: list[Role]
    plan: Plan
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Validade do token em segundos.")
    user: UserOut


class UpdateMeRequest(ApiModel):
    name: NameStr | None = None
    last_name: NameStr | None = None
    email: EmailStr | None = None
    current_password: str | None = Field(
        default=None, description="Obrigatória apenas para trocar o email."
    )

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str | None) -> str | None:
        return v.lower() if v else v


class ChangePasswordRequest(ApiModel):
    current_password: str
    new_password: PasswordStr


class DeleteAccountRequest(ApiModel):
    password: str


class AdminUserUpdate(ApiModel):
    roles: list[Role] | None = Field(default=None, min_length=1)
    plan: Plan | None = None
    is_active: bool | None = None
