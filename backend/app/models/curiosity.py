from datetime import datetime

from pydantic import BaseModel, Field

from app.models.common import ApiModel, ModerationStatus, Source, UserSummary


class CuriosityCreate(ApiModel):
    text: str = Field(min_length=10, max_length=2000)


class CuriosityOut(BaseModel):
    id: str
    landmark_id: str
    landmark_name: str | None = None
    text: str
    author: UserSummary | None = Field(
        default=None, description="Nulo para conteúdo importado ou de conta excluída."
    )
    source: Source | None = None
    status: ModerationStatus
    rejection_reason: str | None = None
    created_at: datetime
