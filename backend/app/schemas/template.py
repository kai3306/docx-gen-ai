from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TemplateGroupCreate(BaseModel):
    name: str
    description: str = ""


class TemplateGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TemplateGroupResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentTemplateResponse(BaseModel):
    id: int
    group_id: int
    name: str
    doc_type: str
    file_name: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateGroupDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    templates: list[DocumentTemplateResponse] = []

    class Config:
        from_attributes = True
