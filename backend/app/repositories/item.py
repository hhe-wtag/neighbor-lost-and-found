from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.item import Item, ItemStatus, ItemType, ItemCategory
from app.repositories.base import BaseRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Item, session)

    async def get_by_id_with_user(self, id: int) -> Optional[Item]:
        result = await self.session.execute(
            select(Item).options(selectinload(Item.user)).where(Item.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_filtered(
        self,
        *,
        type: Optional[ItemType] = None,
        category: Optional[ItemCategory] = None,
        status: Optional[ItemStatus] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Item]:
        query = select(Item).options(selectinload(Item.user))

        if type:
            query = query.where(Item.type == type)
        if category:
            query = query.where(Item.category == category)
        if status:
            query = query.where(Item.status == status)
        else:
            query = query.where(Item.status == ItemStatus.OPEN)

        query = query.order_by(Item.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_by_user(self, user_id: int) -> Sequence[Item]:
        result = await self.session.execute(
            select(Item).where(Item.user_id == user_id).order_by(Item.created_at.desc())
        )
        return result.scalars().all()
