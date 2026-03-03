from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.item_claim import ClaimStatus


class ClaimCreate(BaseModel):
    message: str


class ClaimUpdate(BaseModel):
    message: str


class ClaimedItemResponse(BaseModel):
    id: int
    title: str

    model_config = {"from_attributes": True}


class ClaimantUserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class ClaimResponse(BaseModel):
    id: int
    item_id: int
    claimant_user_id: int
    message: str
    status: ClaimStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ClaimListResponse(BaseModel):
    id: int
    item_id: int
    claimant_user_id: int
    message: Optional[str]
    status: ClaimStatus
    created_at: datetime
    claimant: ClaimantUserResponse

    model_config = {"from_attributes": True}


class MyClaimResponse(BaseModel):
    """
    Response schema for the authenticated user's own claim on an item.
    Excludes `claimant` since the caller is already known to be the claimant.
    """

    id: int
    item_id: int
    message: str
    status: ClaimStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
