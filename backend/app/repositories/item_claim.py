from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.item_claim import ItemClaim, ClaimStatus
from app.repositories.base import BaseRepository
from app.schemas.item_claim import ClaimCreate, ClaimUpdate


class ClaimRepository(BaseRepository[ItemClaim, ClaimCreate, ClaimUpdate]):
    """
    Repository for managing ItemClaim persistence.

    Extends BaseRepository with claim-specific queries such as
    duplicate detection and resolved claim lookups.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(ItemClaim, session)

    async def create(self, schema: ClaimCreate, **kwargs) -> ItemClaim:
        """
        Persist a new claim to the database.
        """
        claim = ItemClaim(
            **schema.model_dump(mode="python"),
            item_id=kwargs["item_id"],
            claimant_user_id=kwargs["claimant_user_id"],
        )
        self.session.add(claim)
        await self.session.flush()
        await self.session.commit()
        return await self.get_by_id(claim.id)

    async def get_all_by_item(self, item_id: int) -> list[ItemClaim]:
        """
        Fetch all claims for an item, with claimant eagerly loaded.

        Used by the service when the requesting user is the item owner
        and needs to review all submitted claims.
        """
        result = await self.session.execute(
            select(ItemClaim)
            .options(selectinload(ItemClaim.claimant))
            .where(ItemClaim.item_id == item_id)
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
            select(ItemClaim).where(
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
                ItemClaim.status.in_([ClaimStatus.APPROVED]),
            )
        )
        return result.scalar_one_or_none()
