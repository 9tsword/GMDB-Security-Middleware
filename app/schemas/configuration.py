from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConfigurationBase(BaseModel):
    key: str = Field(..., min_length=2)
    value: str
    description: Optional[str]


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    value: Optional[str]
    description: Optional[str]


class ConfigurationOut(ConfigurationBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True
