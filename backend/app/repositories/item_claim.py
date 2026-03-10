from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.models.claim_message import ClaimMessage
from app.models.item_claim import ClaimStatus, ItemClaim
from app.repositories.base import BaseRepository
from app.schemas.item_claim import ClaimCreate


def _claim_options():
    """Shared eager-load options for all claim queries."""
    return [
        selectinload(ItemClaim.claimant),
        selectinload(ItemClaim.item),
        selectinload(ItemClaim.messages).selectinload(ClaimMessage.sender),
    ]


class ClaimRepository(BaseRepository[ItemClaim, ClaimCreate, BaseModel]):
    """
    Repository for managing ItemClaim persistence.

    Extends BaseRepository with claim-specific queries such as
    duplicate detection and resolved claim lookups.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(ItemClaim, session)

    async def get_by_id(self, id: int) -> Optional[ItemClaim]:
        """Override base to eager-load all relationships including message thread."""
        result = await self.session.execute(
            select(ItemClaim).options(*_claim_options()).where(ItemClaim.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, schema: ClaimCreate, **kwargs) -> ItemClaim:
        """
        Persist a new claim to the database.
        opening_message is excluded here — it is written to claim_messages
        by the service after the claim is created.
        """
        claim = ItemClaim(
            item_id=kwargs["item_id"],
            claimant_user_id=kwargs["claimant_user_id"],
        )
        self.session.add(claim)
        await self.session.flush()
        await self.session.commit()
        return await self.get_by_id(claim.id)

    async def get_all_by_item(self, item_id: int) -> list[ItemClaim]:
        """
        Fetch all claims for an item with all relationships eager-loaded.

        Used by the service when the requesting user is the item owner
        and needs to review all submitted claims.
        """
        result = await self.session.execute(
            select(ItemClaim)
            .options(*_claim_options())
            .where(ItemClaim.item_id == item_id)
            .order_by(ItemClaim.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_item_and_claimant(
        self, item_id: int, claimant_user_id: int
    ) -> Optional[ItemClaim]:
        """
        Check whether a user has already submitted a claim for a specific item.

        Used by the service layer to enforce the one-claim-per-user-per-item rule.
        """
        result = await self.session.execute(
            select(ItemClaim)
            .options(*_claim_options())
            .where(
                ItemClaim.item_id == item_id,
                ItemClaim.claimant_user_id == claimant_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_resolved_claim_for_item(self, item_id: int) -> Optional[ItemClaim]:
        """
        Retrieve the approved claim for an item, if one exists.

        Used to prevent new claims from being submitted once an item
        has already been matched to a claimant.
        """
        result = await self.session.execute(
            select(ItemClaim).where(
                ItemClaim.item_id == item_id,
                ItemClaim.status == ClaimStatus.APPROVED,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_claimant(self, claimant_user_id: int) -> list[ItemClaim]:
        """All claims submitted by a user — for the claimant's own history."""
        result = await self.session.execute(
            select(ItemClaim)
            .options(*_claim_options())
            .where(ItemClaim.claimant_user_id == claimant_user_id)
            .order_by(ItemClaim.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(
        self, claim: ItemClaim, status: ClaimStatus, resolved_at=None
    ) -> ItemClaim:
        claim.status = status
        if resolved_at:
            claim.resolved_at = resolved_at
        await self.session.flush()
        await self.session.commit()
        return await self.get_by_id(claim.id)