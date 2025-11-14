from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class BackupRecordCreate(BaseModel):
    notes: Optional[str]
    payload: Dict[str, Any]


class BackupRecordOut(BaseModel):
    id: int
    created_at: datetime
    created_by: str
    notes: Optional[str]
    payload: Dict[str, Any]

    class Config:
        orm_mode = True
