# app/schemas/base_response.py

from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: str

    model_config = {"from_attributes": True}


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    total_pages: int
    offset: int
    limit: int
    has_next: bool
    has_prev: bool
