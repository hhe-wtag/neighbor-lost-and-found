from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.item import Item, ItemStatus, ItemType, ItemCategory
from app.models.item_photo import ItemPhoto
from app.repositories.base import BaseRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Item, session)

    async def get_by_id_with_user(self, id: int) -> Item:

        photo_exists = (
            select(ItemPhoto.item_id).where(ItemPhoto.item_id == Item.id).exists()
        )

        result = await self.session.execute(
            select(Item, photo_exists.label("has_photo"))
            .options(selectinload(Item.user))
            .where(Item.id == id)
        )
        row = result.one_or_none()
        if row is None:
            return None

        item, has_photo = row
        item.has_photo = has_photo
        return item

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
            query = query.where(Item.status != ItemStatus.REMOVED)

        query = query.order_by(Item.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_by_user(self, user_id: int) -> Sequence[Item]:
        photo_exists = (
            select(ItemPhoto.item_id).where(ItemPhoto.item_id == Item.id).exists()
        )

        result = await self.session.execute(
            select(Item, photo_exists.label("has_photo"))
            .where(Item.user_id == user_id)
            .order_by(Item.created_at.desc())
        )

        items = []
        for item, has_photo in result.all():
            item.has_photo = has_photo
            items.append(item)

        return items

    async def get_all_filtered_paginated(
        self,
        *,
        type: Optional[ItemType] = None,
        category: Optional[ItemCategory] = None,
        status: Optional[ItemStatus] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Item], int]:
        base_query = select(Item)

        if type:
            base_query = base_query.where(Item.type == type)
        if category:
            base_query = base_query.where(Item.category == category)
        if status:
            base_query = base_query.where(Item.status == status)
        else:
            base_query = base_query.where(Item.status != ItemStatus.REMOVED)

        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()

        photo_exists = (
            select(ItemPhoto.item_id).where(ItemPhoto.item_id == Item.id).exists()
        )

        items_result = await self.session.execute(
            base_query.add_columns(photo_exists.label("has_photo"))
            .options(selectinload(Item.user))
            .order_by(Item.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        items = []
        for item, has_photo in items_result.all():
            item.has_photo = has_photo
            items.append(item)

        return items, total
