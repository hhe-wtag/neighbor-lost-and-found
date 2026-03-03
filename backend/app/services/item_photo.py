from fastapi import UploadFile

from app.core.exception import ForbiddenException, NotFoundException
from app.models.item_photo import ItemPhoto
from app.repositories.item_photo import ItemPhotoRepository
from app.repositories.item import ItemRepository

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


class ItemPhotoService:
    def __init__(self, photo_repo: ItemPhotoRepository, item_repo: ItemRepository):
        self.photo_repo = photo_repo
        self.item_repo = item_repo

    async def upload_photo(
        self, item_id: int, file: UploadFile, current_user_id: int
    ) -> ItemPhoto:
        """
        Upload or replace the photo for an item.
        If a photo already exists it is deleted and replaced automatically.
        Raises ValueError for invalid file type or size.
        """
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("Item not found")
        if item.user_id != current_user_id:
            raise ForbiddenException(
                "You do not have permission to upload a photo for this item"
            )

        if file.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Invalid file type '{file.content_type}'. Allowed: jpeg, png, webp"
            )

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise ValueError("File size exceeds the 5MB limit")

        existing = await self.photo_repo.get_by_item_id(item_id)
        if existing:
            await self.photo_repo.delete(existing)

        return await self.photo_repo.create(item_id, contents, file.content_type)

    async def get_photo_or_404(self, item_id: int) -> ItemPhoto:
        """Fetch the photo for an item, raises 404 if none exists."""
        photo = await self.photo_repo.get_by_item_id(item_id)
        if not photo:
            raise NotFoundException("No photo found for this item")
        return photo

    async def delete_photo(self, item_id: int, current_user_id: int) -> None:
        """Delete the photo for an item. Raises 403 if not owner, 404 if no photo exists."""
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("Item not found")
        if item.user_id != current_user_id:
            raise ForbiddenException("You do not have permission to delete this photo")

        photo = await self.photo_repo.get_by_item_id(item_id)
        if not photo:
            raise NotFoundException("No photo found for this item")

        await self.photo_repo.delete(photo)
