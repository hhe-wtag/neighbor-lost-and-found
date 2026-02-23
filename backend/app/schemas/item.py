from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.item import ItemCategory, ItemStatus, ItemType


class ItemCreate(BaseModel):
    type: ItemType
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: ItemCategory
    date_occurred: Optional[date] = None
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=255)

    @field_validator("date_occurred")
    @classmethod
    def date_not_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("date_occurred cannot be in the future")
        return v


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[ItemCategory] = None
    date_occurred: Optional[date] = None
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=255)
    status: Optional[ItemStatus] = None


class ItemOwnerResponse(BaseModel):
    id: int
    name: Optional[str]
    email: str

    model_config = {"from_attributes": True}


class ItemResponse(BaseModel):
    id: int
    user_id: int
    type: ItemType
    title: str
    description: Optional[str]
    category: ItemCategory
    date_occurred: Optional[date]
    lat: float
    lng: float
    location_name: Optional[str]
    status: ItemStatus
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    user: ItemOwnerResponse

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    id: int
    user_id: int
    type: ItemType
    title: str
    category: ItemCategory
    lat: float
    lng: float
    location_name: Optional[str]
    status: ItemStatus
    created_at: datetime

    model_config = {"from_attributes": True}
