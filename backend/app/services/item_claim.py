from datetime import datetime, UTC
from typing import List

from app.core.exception import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.claim_message import ClaimMessage
from app.models.item import ItemStatus
from app.models.item_claim import ClaimStatus, ItemClaim
from app.repositories.claim_message import ClaimMessageRepository
from app.repositories.item_claim import ClaimRepository
from app.repositories.item import ItemRepository
from app.schemas.item_claim import ClaimCreate, ClaimResolve, MessageCreate


class ItemClaimService:
    def __init__(
        self,
        claim_repo: ClaimRepository,
        message_repo: ClaimMessageRepository,
        item_repo: ItemRepository,
    ):
        self.claim_repo = claim_repo
        self.message_repo = message_repo
        self.item_repo = item_repo

    # ------------------------------------------------------------------
    # Claims
    # ------------------------------------------------------------------

    async def create_claim(
        self, item_id: int, current_user_id: int, payload: ClaimCreate
    ) -> ItemClaim:
        """
        Handle the business logic for creating a claim on an item.
        The opening_message is posted as the first message in the thread.
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

        claim = await self.claim_repo.create(
            schema=payload,
            item_id=item_id,
            claimant_user_id=current_user_id,
        )

        # Post the opening_message as the first message in the thread
        await self.message_repo.create(
            claim.id, current_user_id, payload.opening_message
        )

        # Re-fetch so the opening message is included in the response
        return await self.claim_repo.get_by_id(claim.id)

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

    async def get_claim_or_404(self, claim_id: int) -> ItemClaim:
        claim = await self.claim_repo.get_by_id(claim_id)
        if not claim:
            raise NotFoundException("Claim not found")
        return claim

    async def update_claim(
        self, claim_id: int, current_user_id: int, payload: ClaimUpdate
    ) -> ItemClaim:
        """
        Update claim message for an item by the claimant.
        Only the claimant can edit their own pending claim.
        """
        claim = await self.get_claim_or_404(claim_id)

        if claim.claimant_user_id != current_user_id:
            raise BadRequestException("You cannot edit other users claims")

        if claim.status != ClaimStatus.PENDING:
            raise BadRequestException("Only pending claims can be edited")

        return await self.claim_repo.update(claim, payload)

    async def resolve_claim(
        self, claim_id: int, current_user_id: int, payload: ClaimResolve
    ) -> ItemClaim:
        """
        Approve or reject a claim.
        Only the item owner can resolve claims.
        Approving sets item to CLAIMED, rejecting resets item to OPEN.
        """
        claim = await self.get_claim_or_404(claim_id)
        item = await self.item_repo.get_by_id(claim.item_id)

        if item.user_id != current_user_id:
            raise ForbiddenException("Only the item owner can resolve claims")

        now = datetime.now(UTC)

        if payload.status == ClaimStatus.APPROVED:
            item.status = ItemStatus.CLAIMED
            await self.item_repo.session.flush()
        else:
            item.status = ItemStatus.OPEN
            await self.item_repo.session.flush()

        return await self.claim_repo.update_status(
            claim, payload.status, resolved_at=now
        )

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    async def get_messages(
        self, claim_id: int, current_user_id: int
    ) -> list[ClaimMessage]:
        """
        Fetch the full message thread.
        Only the claimant and item owner can read messages.
        """
        claim = await self.get_claim_or_404(claim_id)
        item = await self.item_repo.get_by_id(claim.item_id)
        self._assert_participant(claim, item, current_user_id)
        return await self.message_repo.get_by_claim_id(claim_id)

    async def send_message(
        self, claim_id: int, current_user_id: int, payload: MessageCreate
    ) -> ClaimMessage:
        """
        Send a message in a claim thread.
        Only the claimant and item owner can send messages.
        Thread is locked once the claim is no longer pending.
        """
        claim = await self.get_claim_or_404(claim_id)
        item = await self.item_repo.get_by_id(claim.item_id)
        self._assert_participant(claim, item, current_user_id)

        if claim.status != ClaimStatus.PENDING:
            raise BadRequestException("Messages can only be sent on pending claims")

        return await self.message_repo.create(claim_id, current_user_id, payload.body)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _assert_participant(claim: ItemClaim, item, user_id: int) -> None:
        """Raise 403 if the user is neither the claimant nor the item owner."""
        if user_id not in (claim.claimant_user_id, item.user_id):
            raise ForbiddenException("You do not have access to this claim")
