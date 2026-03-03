from fastapi import APIRouter
from starlette import status

from app.api.v1.deps import ItemClaimServiceDep, CurrentUserDep
from app.schemas.base_response import APIResponse
from app.schemas.item_claim import ClaimCreate, ClaimResponse

router = APIRouter(prefix="/items", tags=["Claims"])


# ------------------------------------------------------------------
# POST /items/{item_id}/claims
# ------------------------------------------------------------------
@router.post(
    "/claim",
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

    Args:
        item_id (int): The ID of the item to claim (from path).
        payload (ClaimCreate): Claim details submitted by the user.
        service (ItemClaimServiceDep): Injected service handling claim business logic.
        current_user (CurrentUserDep): The authenticated user making the request.

    Returns:
        APIResponse[ClaimResponse]: A success response containing the created claim.

    Raises:
        NotFoundException: 404 if the item does not exist.
        BadRequestException: 400 if the item is not open, already resolved,
            the user owns the item, or a duplicate claim is detected.
    """
    claim = await service.create_claim(item_id, current_user.id, payload)
    return {"success": True, "data": claim, "message": "Claim submitted successfully."}
