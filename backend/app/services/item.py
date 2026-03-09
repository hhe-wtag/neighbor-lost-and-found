import math
from datetime import datetime, UTC
from typing import Optional, Sequence

from app.core.exception import ForbiddenException, NotFoundException
from app.models.item import Item, ItemCategory, ItemStatus, ItemType
from app.repositories.item import ItemRepository
from app.schemas.base_response import PaginatedData
from app.schemas.item import ItemCreate, ItemUpdate, ItemListResponse

EARTH_RADIUS_KM = 6371.0


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in km between two (lat, lng) points."""
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


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
    # List items with optional filters, keyword search, and radius search
    # ------------------------------------------------------------------
    async def list_items_paginated(
        self,
        *,
        type: Optional[ItemType] = None,
        category: Optional[ItemCategory] = None,
        status: Optional[ItemStatus] = None,
        keyword: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius_km: Optional[float] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> PaginatedData[ItemListResponse]:

        # --- Radius pre-filter (business logic, kept in service) ---
        # Fetch ALL unfiltered items to compute distances, then pass the
        # matched IDs (sorted by distance) into the repository. This keeps
        # all geospatial logic out of SQL and in pure Python.
        item_ids: Optional[list[int]] = None
        order_by_ids: Optional[list[int]] = None
        distances: dict[int, float] = {}

        if lat is not None and lng is not None and radius_km is not None:
            all_items = await self.repo.get_all_filtered(
                type=type,
                category=category,
                status=status,
            )

            nearby = []
            for item in all_items:
                d = _haversine(lat, lng, float(item.lat), float(item.lng))
                if d <= radius_km:
                    distances[item.id] = round(d, 3)
                    nearby.append(item.id)

            # Sort by distance ascending so the repository can preserve that order
            nearby.sort(key=lambda id: distances[id])
            item_ids = nearby
            order_by_ids = nearby

        # Normalise keyword for the repository
        normalised_keyword = keyword.strip().lower() if keyword else None

        items, total = await self.repo.get_all_filtered_paginated(
            type=type,
            category=category,
            status=status,
            keyword=normalised_keyword,
            item_ids=item_ids,
            order_by_ids=order_by_ids,
            offset=offset,
            limit=limit,
        )

        # Build responses, stamping distance_km where available
        validated_items = []
        for item in items:
            response = ItemListResponse.model_validate(item)
            if item.id in distances:
                response.distance_km = distances[item.id]
            validated_items.append(response)

        return PaginatedData(
            items=validated_items,
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

        if payload.status == ItemStatus.RESOLVED and item.status != ItemStatus.RESOLVED:
            payload = payload.model_copy(update={"resolved_at": datetime.now(UTC)})

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
