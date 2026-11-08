"""Configuração da aplicação, lida exclusivamente de variáveis de ambiente."""
from enum import StrEnum
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENV: Environment = Environment.DEVELOPMENT
    APP_NAME: str = "Hist API"
    APP_VERSION: str = "1.0.0"
    DOCS_ENABLED: bool = True
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    # Banco de dados
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "hist"

    # Redis (pub/sub do chat). Vazio = broker em memória (apenas 1 processo).
    REDIS_URL: str = ""

    # Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"

    # Autenticação
    JWT_SECRET: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Administrador inicial (criado no startup se ainda não existir)
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = "Administrador"

    # Geolocalização
    NEARBY_DEFAULT_RADIUS_M: int = 200
    NEARBY_MAX_RADIUS_M: int = 50_000
    NEARBY_MAX_RESULTS: int = 200

    # Chat
    CHAT_JOIN_RADIUS_M: int = 200
    CHAT_LEAVE_RADIUS_M: int = 300
    CHAT_MAX_MESSAGE_LENGTH: int = 1000
    CHAT_RATE_LIMIT_MESSAGES: int = 10
    CHAT_RATE_LIMIT_WINDOW_S: int = 10
    # Plano premium: guarda mensagens. Estrutura pronta, desativada por padrão.
    CHAT_PERSISTENCE_ENABLED: bool = False
    CHAT_HISTORY_RETENTION_DAYS: int = 30

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("ADMIN_EMAIL")
    @classmethod
    def _admin_email(cls, value: str) -> str:
        if not value:
            return value
        from pydantic import EmailStr, TypeAdapter

        return TypeAdapter(EmailStr).validate_python(value.strip()).lower()

    @model_validator(mode="after")
    def _check(self):
        if self.CHAT_LEAVE_RADIUS_M < self.CHAT_JOIN_RADIUS_M:
            raise ValueError("CHAT_LEAVE_RADIUS_M deve ser >= CHAT_JOIN_RADIUS_M")
        if bool(self.ADMIN_EMAIL) != bool(self.ADMIN_PASSWORD):
            raise ValueError("ADMIN_EMAIL e ADMIN_PASSWORD devem ser informados juntos")
        if self.ADMIN_PASSWORD and not 8 <= len(self.ADMIN_PASSWORD.encode()) <= 72:
            raise ValueError("ADMIN_PASSWORD deve ter entre 8 e 72 bytes")
        return self

    @property
    def is_production(self) -> bool:
        return self.ENV == Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    return Settings()
