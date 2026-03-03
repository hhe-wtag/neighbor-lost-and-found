from typing import List, Union

from fastapi import APIRouter
from starlette import status

from app.api.v1.deps import ItemClaimServiceDep, CurrentUserDep
from app.schemas.base_response import APIResponse
from app.schemas.item_claim import (
    ClaimCreate,
    ClaimResponse,
    MyClaimResponse,
    ClaimListResponse,
)

router = APIRouter(prefix="/items", tags=["Claims"])


# ------------------------------------------------------------------
# POST /items/{item_id}/claims
# ------------------------------------------------------------------
@router.post(
    "/{item_id}/claim",
    response_model=APIResponse[ClaimResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a claim on an item",
    response_description="The newly created claim object",
)
async def create_claim(
    item_id: int,
    payload: ClaimCreate,
    service: ItemClaimServiceDep,
    current_user: CurrentUserDep,
):
    """
    Submit a claim on a lost/found item.

    Validates that the item exists, is open for claims, and that the
    current user has not already submitted a claim for it. Only one
    resolved claim is allowed per item.
    """
    claim = await service.create_claim(item_id, current_user.id, payload)
    return {"success": True, "data": claim, "message": "Claim submitted successfully."}


# ------------------------------------------------------------------
# GET /items/{item_id}/claims — list claims for an item (owner or claimant)
# ------------------------------------------------------------------
@router.get(
    "/{item_id}/claims",
    response_model=APIResponse[Union[List[ClaimListResponse], MyClaimResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get user's claim on an item",
    response_description="The user's claim on an item",
)
async def get_claims_for_an_item(
    item_id: int,
    service: ItemClaimServiceDep,
    current_user: CurrentUserDep,
):
    """Get claims on an item. The owner can see all the claims of an item.
    The claimant can only see their own claim on an item."""
    claims = await service.get_claims_for_an_item(item_id, current_user.id)
    return {
        "success": True,
        "data": claims,
        "message": "Claims retrieved successfully.",
    }
