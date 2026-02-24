from typing import Optional

from fastapi import APIRouter, Query, status

from app.api.v1.deps import ItemServiceDep, CurrentUserDep
from app.models.item import ItemCategory, ItemStatus, ItemType
from app.schemas.base_response import APIResponse
from app.schemas.item import (
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemUpdate,
)


router = APIRouter(prefix="/items", tags=["Items"])


# ------------------------------------------------------------------
# POST /items — report a lost or found item
# ------------------------------------------------------------------
@router.post(
    "/", response_model=APIResponse[ItemResponse], status_code=status.HTTP_201_CREATED
)
async def create_item(
    payload: ItemCreate,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
):
    item = await service.create_item(payload, current_user.id)

    return {
        "success": True,
        "data": item,
        "message": "Item reported successfully.",
    }


# ------------------------------------------------------------------
# GET /items — browse listings with optional filters
# ------------------------------------------------------------------
@router.get("/", response_model=APIResponse[list[ItemListResponse]])
async def list_items(
    service: ItemServiceDep,
    type: Optional[ItemType] = Query(None),
    category: Optional[ItemCategory] = Query(None),
    status: Optional[ItemStatus] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    items = await service.list_items(
        type=type,
        category=category,
        status=status,
        offset=offset,
        limit=limit,
    )

    return {
        "success": True,
        "data": items,
        "message": "Items retrieved successfully.",
    }


# ------------------------------------------------------------------
# GET /items/me — current user's own listings
# ------------------------------------------------------------------
@router.get("/me", response_model=APIResponse[list[ItemListResponse]])
async def list_my_items(
    service: ItemServiceDep,
    current_user: CurrentUserDep,
):
    items = await service.list_user_items(current_user.id)

    return {
        "success": True,
        "data": items,
        "message": "Your items retrieved successfully.",
    }


# ------------------------------------------------------------------
# GET /items/categories — all allowed item categories
# ------------------------------------------------------------------
@router.get("/categories", response_model=APIResponse[list[ItemCategory]])
async def get_categories():
    return {
        "success": True,
        "data": list(ItemCategory),
        "message": "Available categories retrieved successfully.",
    }


# ------------------------------------------------------------------
# GET /items/{item_id} — single item detail
# ------------------------------------------------------------------
@router.get("/{item_id}", response_model=APIResponse[ItemResponse])
async def get_item(item_id: int, service: ItemServiceDep):
    item = await service.get_item_or_404(item_id)

    return {
        "success": True,
        "data": item,
        "message": "Item retrieved successfully.",
    }


# ------------------------------------------------------------------
# PATCH /items/{item_id} — edit your own item
# ------------------------------------------------------------------
@router.patch(
    "/{item_id}",
    response_model=APIResponse[ItemResponse],
)
async def update_item(
    item_id: int,
    payload: ItemUpdate,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
):
    item = await service.update_item(item_id, payload, current_user.id)

    return {
        "success": True,
        "data": item,
        "message": "Item updated successfully.",
    }


# ------------------------------------------------------------------
# DELETE /items/{item_id} — delete own item
# ------------------------------------------------------------------
@router.delete("/{item_id}", response_model=APIResponse[None])
async def delete_item(
    item_id: int,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
):
    await service.remove_item(item_id, current_user.id)

    return {
        "success": True,
        "data": None,
        "message": "Item removed successfully.",
    }
