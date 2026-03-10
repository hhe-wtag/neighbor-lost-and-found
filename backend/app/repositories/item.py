from typing import Optional, Sequence

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
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
        keyword: Optional[str] = None,
        item_ids: Optional[list[int]] = None,
        order_by_ids: Optional[list[int]] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Item], int]:
        """
        Paginated item query.

        - keyword: pre-validated by the service, applied as a case-insensitive
          LIKE across title and description.
        - item_ids: when provided (radius search), restricts results to this set.
        - order_by_ids: when provided, results are returned in this exact order
          (distance-ascending pre-sorted by the service).
        """
        base_query = select(Item)

        if type:
            base_query = base_query.where(Item.type == type)
        if category:
            base_query = base_query.where(Item.category == category)
        if status:
            base_query = base_query.where(Item.status == status)
        else:
            base_query = base_query.where(Item.status != ItemStatus.REMOVED)

        if keyword:
            term = f"%{keyword}%"
            base_query = base_query.where(
                or_(
                    func.lower(Item.title).like(term),
                    func.lower(Item.description).like(term),
                )
            )

        if item_ids is not None:
            if not item_ids:
                # No items matched the radius filter — return early
                return [], 0
            base_query = base_query.where(Item.id.in_(item_ids))

        # Count before pagination
        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()

        photo_exists = (
            select(ItemPhoto.item_id).where(ItemPhoto.item_id == Item.id).exists()
        )

        # Ordering: preserve distance order from service if provided, else recency
        if order_by_ids:
            id_order = {id: idx for idx, id in enumerate(order_by_ids)}
            items_result = await self.session.execute(
                base_query.add_columns(photo_exists.label("has_photo"))
                .options(selectinload(Item.user))
                .offset(offset)
                .limit(limit)
            )
            rows = items_result.all()
            rows.sort(key=lambda row: id_order.get(row[0].id, float("inf")))
        else:
            items_result = await self.session.execute(
                base_query.add_columns(photo_exists.label("has_photo"))
                .options(selectinload(Item.user))
                .order_by(Item.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            rows = items_result.all()

        items = []
        for item, has_photo in rows:
            item.has_photo = has_photo
            items.append(item)

        return items, total
