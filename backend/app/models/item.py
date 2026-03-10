import enum
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum,
    Date,
    Numeric,
    Integer,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ItemType(enum.Enum):
    LOST = "lost"
    FOUND = "found"


class ItemCategory(enum.Enum):
    ELECTRONICS = "electronics"
    PETS = "pets"
    KEYS = "keys"
    WALLET = "wallet"
    BAG = "bag"
    DOCUMENTS = "documents"
    CLOTHING = "clothing"
    JEWELRY = "jewelry"
    OTHER = "other"


class ItemStatus(enum.Enum):
    OPEN = "open"
    CLAIMED = "claimed"
    RESOLVED = "resolved"
    REMOVED = "removed"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[ItemCategory] = mapped_column(Enum(ItemCategory), nullable=False)

    date_occurred: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)

    lat: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    lng: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), default=ItemStatus.OPEN, nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None, nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="items")

    photo: Mapped[Optional["ItemPhoto"]] = relationship(
        "ItemPhoto", back_populates="item", uselist=False, cascade="all, delete-orphan"
    )

    claims: Mapped[list["ItemClaim"]] = relationship(
        "ItemClaim", back_populates="item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Item id={self.id} type={self.type!r} title={self.title!r} status={self.status!r}>"
