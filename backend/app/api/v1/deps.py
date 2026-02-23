from typing import Annotated, Optional
from fastapi import Depends, Cookie, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService


# =========================
# Repository Dependencies
# =========================
def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]


# =========================
# Function Dependencies
# ==========================
async def get_session_token(
    session_token: Annotated[Optional[str], Cookie()] = None,
) -> str:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return session_token


SessionTokenDep = Annotated[str, Depends(get_session_token)]


# ==========================
# Service Dependencies
# ==========================
def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(session)
    session_repo = SessionRepository(session)
    return AuthService(user_repo, session_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
