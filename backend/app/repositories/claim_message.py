from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.claim_message import ClaimMessage


class ClaimMessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_claim_id(self, claim_id: int) -> list[ClaimMessage]:
        """Fetch full message thread ordered by created_at asc."""
        result = await self.session.execute(
            select(ClaimMessage)
            .options(selectinload(ClaimMessage.sender))
            .where(ClaimMessage.claim_id == claim_id)
            .order_by(ClaimMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_latest_by_claim_id(self, claim_id: int) -> Optional[ClaimMessage]:
        """Most recent message — used for last_message preview in list views."""
        result = await self.session.execute(
            select(ClaimMessage)
            .options(selectinload(ClaimMessage.sender))
            .where(ClaimMessage.claim_id == claim_id)
            .order_by(ClaimMessage.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, claim_id: int, sender_id: int, body: str) -> ClaimMessage:
        message = ClaimMessage(claim_id=claim_id, sender_id=sender_id, body=body)
        self.session.add(message)
        await self.session.flush()
        await self.session.commit()

        # Re-fetch with sender eager-loaded to avoid MissingGreenlet on serialization
        result = await self.session.execute(
            select(ClaimMessage)
            .options(selectinload(ClaimMessage.sender))
            .where(ClaimMessage.id == message.id)
        )
        return result.scalar_one()