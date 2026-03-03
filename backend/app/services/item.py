import math
from datetime import datetime, UTC
from typing import Optional, Sequence

from app.core.exception import ForbiddenException, NotFoundException
from app.models.item import Item, ItemCategory, ItemStatus, ItemType
from app.repositories.item import ItemRepository
from app.schemas.base_response import PaginatedData
from app.schemas.item import ItemCreate, ItemUpdate, ItemListResponse


class ItemService:
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    # ------------------------------------------------------------------
    # Create a new item (lost or found)
    # ------------------------------------------------------------------
    async def create_item(self, payload: ItemCreate, user_id: int) -> Item:
        return await self.repo.create(payload, user_id=user_id)

    # ------------------------------------------------------------------
    # Fetch a single item or raise NotFound
    # ------------------------------------------------------------------
    async def get_item_or_404(self, item_id: int) -> Item:
        item = await self.repo.get_by_id_with_user(item_id)
        if not item:
            raise NotFoundException("Item not found")
        return item

    # ------------------------------------------------------------------
    # List items with optional filters
    # ------------------------------------------------------------------
    async def list_items_paginated(
        self,
        *,
        type: Optional[ItemType] = None,
        category: Optional[ItemCategory] = None,
        status: Optional[ItemStatus] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> PaginatedData[ItemListResponse]:
        items, total = await self.repo.get_all_filtered_paginated(
            type=type,
            category=category,
            status=status,
            offset=offset,
            limit=limit,
        )

        return PaginatedData(
            items=[ItemListResponse.model_validate(item) for item in items],
            total=total,
            page=(offset // limit) + 1,
            total_pages=math.ceil(total / limit) if total > 0 else 1,
            offset=offset,
            limit=limit,
            has_next=offset + limit < total,
            has_prev=offset > 0,
        )

    # ------------------------------------------------------------------
    # List items belonging to a specific user
    # ------------------------------------------------------------------
    async def list_user_items(self, user_id: int) -> Sequence[Item]:
        return await self.repo.get_all_by_user(user_id)

    # ------------------------------------------------------------------
    # Update an item (only owner can update)
    # ------------------------------------------------------------------
    async def update_item(
        self, item_id: int, payload: ItemUpdate, current_user_id: int
    ) -> Item:
        item = await self.get_item_or_404(item_id)
        self._assert_owner(item, current_user_id)

        # Stamp resolved_at when status transitions to RESOLVED
        if payload.status == ItemStatus.RESOLVED and item.status != ItemStatus.RESOLVED:
            payload = payload.model_copy(
                update={"resolved_at": datetime.now(UTC)}  # type: ignore[arg-type]
            )

        return await self.repo.update(item, payload)

    # ------------------------------------------------------------------
    # Soft-delete an item (mark as REMOVED)
    # ------------------------------------------------------------------
    async def remove_item(self, item_id: int, current_user_id: int) -> None:
        item = await self.get_item_or_404(item_id)
        self._assert_owner(item, current_user_id)

        item.status = ItemStatus.REMOVED
        await self.repo.session.commit()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _assert_owner(item: Item, user_id: int) -> None:
        if item.user_id != user_id:
            raise ForbiddenException("You do not have permission to modify this item")
