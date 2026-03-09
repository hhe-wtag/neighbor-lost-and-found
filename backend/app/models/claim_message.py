from datetime import datetime, UTC
from sqlalchemy import Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClaimMessage(Base):
    __tablename__ = "claim_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    claim: Mapped["ItemClaim"] = relationship("ItemClaim", back_populates="messages")
    sender: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ClaimMessage id={self.id} claim_id={self.claim_id!r} sender_id={self.sender_id!r}>"