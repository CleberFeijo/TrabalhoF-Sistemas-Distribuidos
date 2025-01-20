import os
import pathlib
from pydantic import AnyHttpUrl, Field, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
import pytz

__all__ = "settings", "TIMEZONE",


TIMEZONE = pytz.timezone(os.getenv("TIMEZONE"))


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET: str = Field(default=None, env="JWT_SECRET")

    # Tempo de expiração do token de acesso de usuário.
    # (60 minutos * 24 horas * 7 dias)
    USER_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    # Lista de origins CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    KEY_TO_CREATE_USER: str = os.getenv(
        "CREATE_USER_PASSWORD"
    )

    MONGO_USER: str = ""

    MONGO_PASSWORD: str = ""

    MONGO_HOST: str = ""

    MONGO_PORT: str = ""

    MONGO_DATABASE: str = os.getenv(
        "MONGO_DB_DATABASE_NAME"
    )

    MONGO_DEBUG: str = os.getenv(
        "MONGO_DB_DEBUG"
    )

    def mongo_local(self):
        self.MONGO_USER = os.getenv(
            "MONGO_DB_USER"
        ) or ""

        self.MONGO_PASSWORD = os.getenv(
            "MONGO_DB_PASSWORD"
        ) or ""

        self.MONGO_HOST = os.getenv(
            "MONGO_DB_HOST"
        ) or ""

        self.MONGO_PORT = os.getenv(
            "MONGO_DB_PORT"
        ) or ""

    @property
    def mongo_uri(self):
        self.mongo_local()
        return f'mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}'

    @classmethod
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings()
