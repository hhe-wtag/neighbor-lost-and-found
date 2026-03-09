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
    ClaimResolve,
    ClaimMessageResponse,
    MessageCreate,
)

router = APIRouter(prefix="/items", tags=["Claims"])

# ------------------------------------------------------------------
# GET /items/claims/{claim_id}/messages — fetch full message thread
# ------------------------------------------------------------------
@router.get(
    "/claims/{claim_id}/messages",
    response_model=APIResponse[list[ClaimMessageResponse]],
    summary="Get message thread for a claim",
)
async def get_messages(
    claim_id: int,
    service: ItemClaimServiceDep,
    current_user: CurrentUserDep,
):
    """Fetch the full message thread for a claim. Only the claimant or item owner can read."""
    messages = await service.get_messages(claim_id, current_user.id)
    return {
        "success": True,
        "data": messages,
        "message": "Messages retrieved successfully.",
    }


# ------------------------------------------------------------------
# POST /items/claims/{claim_id}/messages — send a message
# ------------------------------------------------------------------
@router.post(
    "/claims/{claim_id}/messages",
    response_model=APIResponse[ClaimMessageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send a message in a claim thread",
)
async def send_message(
    claim_id: int,
    payload: MessageCreate,
    service: ItemClaimServiceDep,
    current_user: CurrentUserDep,
):
    """Send a message in a claim thread. Locked once the claim is resolved."""
    message = await service.send_message(claim_id, current_user.id, payload)
    return {"success": True, "data": message, "message": "Message sent successfully."}


# ------------------------------------------------------------------
# PATCH /items/claims/{claim_id}/resolve — approve or reject (owner only)
# ------------------------------------------------------------------
@router.patch(
    "/claims/{claim_id}/resolve",
    response_model=APIResponse[ClaimResponse],
)
async def resolve_claim(
    claim_id: int,
    payload: ClaimResolve,
    service: ItemClaimServiceDep,
    current_user: CurrentUserDep,
):
    """Approve or reject a claim. Only the item owner can resolve claims."""
    claim = await service.resolve_claim(claim_id, current_user.id, payload)
    return {
        "success": True,
        "data": claim,
        "message": f"Claim {payload.status.value} successfully.",
    }


# ------------------------------------------------------------------
# POST /items/{item_id}/claim — submit a claim on an item
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


# --------------------------------------------------------------------------
# GET /items/{item_id}/claims — list claims for an item (owner or claimant)
# --------------------------------------------------------------------------
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
