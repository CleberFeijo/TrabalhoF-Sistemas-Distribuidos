from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ModerationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Source(BaseModel):
    """Origem de um conteúdo importado (crawler) ou de referência."""

    name: str = Field(description="Nome da fonte, ex.: 'wikidata', 'wikipedia'.")
    url: str | None = None
    license: str | None = Field(default=None, description="Ex.: 'CC BY-SA 4.0'.")
    external_id: str | None = Field(default=None, description="Identificador na fonte, ex.: 'Q12345'.")
    retrieved_at: datetime | None = None


class UserSummary(BaseModel):
    id: str
    name: str


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class RejectRequest(ApiModel):
    reason: str = Field(min_length=3, max_length=500)


class Message(BaseModel):
    message: str
