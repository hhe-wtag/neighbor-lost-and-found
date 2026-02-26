from datetime import datetime
from pydantic import BaseModel


class ItemPhotoResponse(BaseModel):
    id: int
    item_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
