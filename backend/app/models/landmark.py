from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl

from app.models.common import ApiModel, ModerationStatus, Source

Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


class LandmarkCreate(ApiModel):
    """Sugestão de novo ponto histórico (entra como pendente para usuários comuns)."""

    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    latitude: Latitude
    longitude: Longitude
    category: str | None = Field(default=None, max_length=80)
    address: str | None = Field(default=None, max_length=300)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=60)
    image_url: HttpUrl | None = None
    curiosity: str | None = Field(
        default=None, min_length=10, max_length=2000,
        description="Curiosidade inicial opcional, moderada junto com o ponto.",
    )


class LandmarkUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    category: str | None = Field(default=None, max_length=80)
    address: str | None = Field(default=None, max_length=300)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=60)
    image_url: HttpUrl | None = None


class LandmarkOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    latitude: float
    longitude: float
    category: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    image_url: str | None = None
    source: Source | None = None
    status: ModerationStatus
    rejection_reason: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime
    curiosity_count: int = Field(default=0, description="Curiosidades aprovadas.")


class NearbyLandmark(LandmarkOut):
    distance_m: float = Field(description="Distância em metros até a posição informada.")
    chat_available: bool = Field(
        description="Se o usuário está perto o bastante para entrar no chat deste ponto."
    )
