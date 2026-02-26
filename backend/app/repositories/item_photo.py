from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item_photo import ItemPhoto


class ItemPhotoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_item_id(self, item_id: int) -> Optional[ItemPhoto]:
        result = await self.session.execute(
            select(ItemPhoto).where(ItemPhoto.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def create(self, item_id: int, data: bytes, mime_type: str) -> ItemPhoto:
        photo = ItemPhoto(item_id=item_id, data=data, mime_type=mime_type)
        self.session.add(photo)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(photo)
        return photo

    async def delete(self, photo: ItemPhoto) -> None:
        await self.session.delete(photo)
        await self.session.flush()
        await self.session.commit()
