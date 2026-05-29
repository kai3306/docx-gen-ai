from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class FormFieldDef(BaseModel):
    field_key: str
    label: str
    type: str = "text"  # text, textarea, select, date
    required: bool = False
    options: list[str] = []


class FormTemplateCreate(BaseModel):
    name: str
    description: str = ""
    fields: list[FormFieldDef] = []
    is_base: bool = False
    base_template_id: Optional[int] = None


class FormTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[list[FormFieldDef]] = None
    is_base: Optional[bool] = None
    base_template_id: Optional[int] = None


class FormTemplateResponse(BaseModel):
    id: int
    name: str
    description: str
    fields: Any  # list[FormFieldDef] as JSON
    is_base: bool = False
    base_template_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FormDataCreate(BaseModel):
    form_template_id: int
    project_id: Optional[int] = None
    field_values: dict[str, Any] = {}


class FormDataUpdate(BaseModel):
    field_values: Optional[dict[str, Any]] = None


class FormDataResponse(BaseModel):
    id: int
    form_template_id: int
    project_id: Optional[int]
    field_values: Any  # dict as JSON
    created_at: datetime

    class Config:
        from_attributes = True
