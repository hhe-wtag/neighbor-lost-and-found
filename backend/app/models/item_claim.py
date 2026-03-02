import enum
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import (
    Text,
    DateTime,
    Enum,
    Integer,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClaimStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ItemClaim(Base):
    __tablename__ = "claims"

    __table_args__ = (
        UniqueConstraint("item_id", "claimant_user_id", name="uq_claim_item_claimant"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    claimant_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus), default=ClaimStatus.PENDING, nullable=False
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

    claimant: Mapped["User"] = relationship("User", back_populates="claims")
    item: Mapped["Item"] = relationship("Item", back_populates="claims")

    def __repr__(self) -> str:
        return (
            f"<ItemClaim id={self.id} item_id={self.item_id!r} "
            f"claimant_user_id={self.claimant_user_id!r} status={self.status!r}>"
        )
