from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models import MigrationTaskStatus


class MigrationTaskBase(BaseModel):
    task_id: str = Field(..., min_length=3, max_length=50)
    table_name: str
    field_name: str
    batch_size: int = Field(default=1000, ge=1)
    concurrency: int = Field(default=1, ge=1)
    overwrite_plaintext: bool = False


class MigrationTaskCreate(MigrationTaskBase):
    pass


class MigrationTaskUpdate(BaseModel):
    status: Optional[MigrationTaskStatus]
    progress: Optional[int]
    success_count: Optional[int]
    failure_count: Optional[int]
    failure_reason: Optional[str]


class MigrationTaskOut(MigrationTaskBase):
    id: int
    status: MigrationTaskStatus
    progress: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    success_count: int
    failure_count: int
    failure_reason: Optional[str]
    operator_id: Optional[int]

    class Config:
        orm_mode = True
