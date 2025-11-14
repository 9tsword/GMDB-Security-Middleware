from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SensitiveFieldBase(BaseModel):
    field_id: str = Field(..., min_length=2, max_length=50)
    table_name: str
    field_name: str
    algorithm_type: str
    status: str = "未加密"
    allow_plain_text_read: bool = False
    remarks: Optional[str]
    is_enabled: bool = True


class SensitiveFieldCreate(SensitiveFieldBase):
    pass


class SensitiveFieldUpdate(BaseModel):
    table_name: Optional[str]
    field_name: Optional[str]
    algorithm_type: Optional[str]
    status: Optional[str]
    allow_plain_text_read: Optional[bool]
    remarks: Optional[str]
    is_enabled: Optional[bool]


class SensitiveFieldOut(SensitiveFieldBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
