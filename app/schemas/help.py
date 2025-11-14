from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HelpDocumentBase(BaseModel):
    title: str
    category: Optional[str]
    content: str
    attachment_url: Optional[str]
    version: str = "v1.0.0"


class HelpDocumentCreate(HelpDocumentBase):
    pass


class HelpDocumentUpdate(BaseModel):
    title: Optional[str]
    category: Optional[str]
    content: Optional[str]
    attachment_url: Optional[str]
    version: Optional[str]


class HelpDocumentOut(HelpDocumentBase):
    id: int
    published_at: datetime

    class Config:
        orm_mode = True
