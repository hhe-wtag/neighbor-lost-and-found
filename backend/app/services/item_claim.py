from typing import List

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

    async def get_claims_for_an_item(
        self, item_id: int, current_user_id: int
    ) -> ItemClaim | List[ItemClaim]:
        item = await self.item_repo.get_by_id(item_id)

        if not item:
            raise NotFoundException("Item not found")

        if item.user_id == current_user_id:
            return await self.claim_repo.get_all_by_item(item_id)

        claim = await self.claim_repo.get_by_item_and_claimant(
            item_id=item_id, claimant_user_id=current_user_id
        )

        if not claim:
            return []

        return claim
