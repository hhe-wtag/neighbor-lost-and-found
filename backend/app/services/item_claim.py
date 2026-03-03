from app.core.exception import NotFoundException, BadRequestException
from app.models.item import ItemStatus
from app.models.item_claim import ItemClaim
from app.repositories.item_claim import ClaimRepository
from app.repositories.item import ItemRepository
from app.schemas.item_claim import ClaimCreate


class ItemClaimService:
    def __init__(self, claim_repo: ClaimRepository, item_repo: ItemRepository):
        self.claim_repo = claim_repo
        self.item_repo = item_repo

    async def create_claim(
        self, item_id: int, current_user_id: int, payload: ClaimCreate
    ) -> ItemClaim:
        """
        Handle the business logic for creating a claim on an item.

        Performs the following validations before creating the claim:
            1. Item must exist.
            2. Item status must be OPEN.
            3. The claimant must not be the item owner.
            4. The user must not have an existing claim on this item.
            5. The item must not already have an approved/resolved claim.

        Args:
            item_id (int): The ID of the item being claimed.
            current_user_id (int): The ID of the user submitting the claim.
            payload (ClaimCreate): The claim data provided by the user.

        Returns:
            ItemClaim: The newly created claim ORM object.

        Raises:
            NotFoundException: If no item with the given ID exists.
            BadRequestException: If any of the business rule validations fail.
        """
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("Item not found")

        # Claims are only accepted on items that are still open
        if item.status != ItemStatus.OPEN:
            raise BadRequestException("Only open items can be claimed")

        # Prevent owners from claiming their own reported item
        if item.user_id == current_user_id:
            raise BadRequestException("You cannot claim your own item")

        # Enforce one claim per user per item
        existing = await self.claim_repo.get_by_item_and_claimant(
            item_id=item.id, claimant_user_id=current_user_id
        )
        if existing:
            raise BadRequestException(
                "You have already submitted a claim for this item"
            )

        # Block further claims once one has already been approved
        resolved = await self.claim_repo.get_resolved_claim_for_item(item_id)
        if resolved:
            raise BadRequestException("This item already has a claim already resolved")

        return await self.claim_repo.create(
            schema=payload,
            item_id=item_id,
            claimant_user_id=current_user_id,
        )
