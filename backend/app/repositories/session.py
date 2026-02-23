from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate


class SessionRepository(BaseRepository[Session, SessionCreate, SessionUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Session, session)

    async def get_by_token(self, session_token: str) -> Optional[Session]:
        result = await self.session.execute(
            select(self.model).where(self.model.session_token == session_token)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[Session]:
        result = await self.session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create_session(
        self, user_id: int, session_token: str, expires_at: datetime
    ) -> Session:
        schema = SessionCreate(
            user_id=user_id, session_token=session_token, expires_at=expires_at
        )
        return await self.create(schema)

    async def invalidate(self, session: Session) -> None:
        await self.delete(session)

    async def invalidate_all_user_sessions(self, user_id: int) -> None:
        sessions = await self.get_by_user_id(user_id)
        for session in sessions:
            await self.delete(session)

    async def is_valid(self, session: Session) -> bool:
        return session.expires_at > datetime.now(UTC)
