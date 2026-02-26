from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CurrentUserDep
from app.core.database import get_db
from app.core.exception import BadRequestException
from app.repositories.item_photo import ItemPhotoRepository
from app.repositories.item import ItemRepository
from app.schemas.base_response import APIResponse
from app.schemas.item_photo import ItemPhotoResponse
from app.services.item_photo import ItemPhotoService

router = APIRouter(prefix="/items", tags=["Item Photos"])


def get_photo_service(db: AsyncSession = Depends(get_db)) -> ItemPhotoService:
    return ItemPhotoService(
        photo_repo=ItemPhotoRepository(db),
        item_repo=ItemRepository(db),
    )


PhotoServiceDep = Depends(get_photo_service)


# ------------------------------------------------------------------
# GET /items/{item_id}/photo — serve the photo bytes
# ------------------------------------------------------------------
@router.get("/{item_id}/photo")
async def get_photo(
    item_id: int,
    service: ItemPhotoService = PhotoServiceDep,
):
    """Stream the photo for an item directly as an image response."""
    photo = await service.get_photo_or_404(item_id)
    return Response(content=photo.data, media_type=photo.mime_type)


# ------------------------------------------------------------------
# PUT /items/{item_id}/photo — upload or replace photo
# ------------------------------------------------------------------
@router.put(
    "/{item_id}/photo",
    response_model=APIResponse[ItemPhotoResponse],
    status_code=status.HTTP_200_OK,
)
async def upload_photo(
    item_id: int,
    current_user: CurrentUserDep,
    file: UploadFile = File(...),
    service: ItemPhotoService = PhotoServiceDep,
):
    """Upload or replace the photo for an item. Uploading automatically removes any existing photo."""
    try:
        photo = await service.upload_photo(item_id, file, current_user.id)
    except ValueError as e:
        raise BadRequestException(str(e))

    return {"success": True, "data": photo, "message": "Photo uploaded successfully."}


# ------------------------------------------------------------------
# DELETE /items/{item_id}/photo — remove photo
# ------------------------------------------------------------------
@router.delete(
    "/{item_id}/photo",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_photo(
    item_id: int,
    current_user: CurrentUserDep,
    service: ItemPhotoService = PhotoServiceDep,
):
    """Delete the photo for an item from the database."""
    await service.delete_photo(item_id, current_user.id)

    return {
        "success": True,
        "data": None,
        "message": "Photo deleted successfully.",
    }
