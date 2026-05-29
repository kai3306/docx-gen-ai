from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    project_number: Optional[str] = ""
    commission_type: Optional[str] = ""
    customer_name: Optional[str] = ""
    description: Optional[str] = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    project_number: Optional[str] = None
    commission_type: Optional[str] = None
    customer_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    project_number: Optional[str]
    commission_type: Optional[str]
    customer_name: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
