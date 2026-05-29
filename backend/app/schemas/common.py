from pydantic import BaseModel
from typing import Any, Optional, List


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    success: bool = True
    items: List[Any]
    total: int
    page: int = 1
    page_size: int = 20
