from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.db.models import AuditLogType


class AuditLogBase(BaseModel):
    log_type: AuditLogType
    username: Optional[str]
    ip_address: Optional[str]
    table_name: Optional[str]
    field_name: Optional[str]
    task_id: Optional[str]
    operation: Optional[str]
    status: Optional[str]
    error_message: Optional[str]

    details: Dict[str, Any] = Field(default_factory=dict)



class AuditLogCreate(AuditLogBase):
    pass


class AuditLogOut(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
