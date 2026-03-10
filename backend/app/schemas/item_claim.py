from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.item_claim import ClaimStatus


class ClaimCreate(BaseModel):
    opening_message: str = Field(..., min_length=1, max_length=1000)


class MessageCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=1000)


class ClaimResolve(BaseModel):
    status: ClaimStatus


class ClaimedItemResponse(BaseModel):
    id: int
    title: str

    model_config = {"from_attributes": True}


class ClaimantUserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class ClaimMessageResponse(BaseModel):
    id: int
    claim_id: int
    sender_id: int
    body: str
    created_at: datetime
    sender: ClaimantUserResponse

    model_config = {"from_attributes": True}


class ClaimResponse(BaseModel):
    id: int
    item_id: int
    claimant_user_id: int
    status: ClaimStatus
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    claimant: ClaimantUserResponse
    item: ClaimedItemResponse
    messages: list[ClaimMessageResponse] = []

    model_config = {"from_attributes": True}


class MyClaimResponse(BaseModel):
    """
    Response schema for the authenticated user's own claim on an item.
    Excludes claimant since the caller is already known to be the claimant.
    """

    id: int
    item_id: int
    status: ClaimStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    item: ClaimedItemResponse
    messages: list[ClaimMessageResponse] = []

    model_config = {"from_attributes": True}


class ClaimListResponse(BaseModel):
    id: int
    item_id: int
    claimant_user_id: int
    status: ClaimStatus
    created_at: datetime
    claimant: ClaimantUserResponse
    item: ClaimedItemResponse
    last_message: Optional[ClaimMessageResponse] = None

    model_config = {"from_attributes": True}
