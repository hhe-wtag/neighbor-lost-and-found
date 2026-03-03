from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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

        Combines the validated schema fields with relational IDs passed
        as keyword arguments, flushes and commits the session, then
        returns the fully hydrated ORM object.

        Args:
            schema (ClaimCreate): Validated claim payload from the request.
            **kwargs:
                item_id (int): The ID of the item being claimed.
                claimant_user_id (int): The ID of the user submitting the claim.

        Returns:
            ItemClaim: The persisted claim fetched fresh from the database.
        """
        claim = ItemClaim(
            **schema.model_dump(mode="python"),
            item_id=kwargs["item_id"],
            claimant_user_id=kwargs["claimant_user_id"],
        )
        self.session.add(claim)
        await self.session.flush()  # Assign DB-generated ID before commit
        await self.session.commit()
        return await self.get_by_id(claim.id)

    async def get_by_item_and_claimant(
        self, item_id: int, claimant_user_id: int
    ) -> Optional[ItemClaim]:
        """
        Check whether a user has already submitted a claim for a specific item.

        Used by the service layer to enforce the one-claim-per-user-per-item rule.

        Args:
            item_id (int): The ID of the item to check.
            claimant_user_id (int): The ID of the user to check against.

        Returns:
            ItemClaim | None: The existing claim if found, otherwise None.
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

        Args:
            item_id (int): The ID of the item to check.

        Returns:
            ItemClaim | None: The approved claim if it exists, otherwise None.
        """
        result = await self.session.execute(
            select(ItemClaim).where(
                ItemClaim.item_id == item_id,
                ItemClaim.status.in_([ClaimStatus.APPROVED]),
            )
        )
        return result.scalar_one_or_none()
