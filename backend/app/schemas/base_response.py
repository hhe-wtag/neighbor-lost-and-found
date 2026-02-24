# app/schemas/base_response.py

from typing import Generic, TypeVar, Optional

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class APIResponse(GenericModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: str


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    total_pages: int
    offset: int
    limit: int
    has_next: bool
    has_prev: bool
