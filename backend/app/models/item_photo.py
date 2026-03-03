from datetime import datetime, UTC
from sqlalchemy import String, DateTime, Integer, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ItemPhoto(Base):
    __tablename__ = "item_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    item: Mapped["Item"] = relationship("Item", back_populates="photo")

    def __repr__(self) -> str:
        return f"<ItemPhoto id={self.id} item_id={self.item_id} mime_type={self.mime_type!r}>"
