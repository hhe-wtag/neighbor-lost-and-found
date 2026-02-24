from typing import Annotated, Optional

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.repositories.item import ItemRepository
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.item import ItemService


# =========================
# Repository Dependencies
# =========================
def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]


# ==========================
# Service Dependencies
# ==========================
def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=UserRepository(session),
        session_repo=SessionRepository(session),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_item_service(session: AsyncSession = Depends(get_db)) -> ItemService:
    return ItemService(ItemRepository(session))


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


# =========================
# Auth Dependencies
# =========================
async def get_session_token(
    session_token: Annotated[Optional[str], Cookie()] = None,
) -> str:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return session_token


SessionTokenDep = Annotated[str, Depends(get_session_token)]


async def get_current_user(
    session_token: SessionTokenDep,
    auth_service: AuthServiceDep,
) -> User:
    return await auth_service.get_current_user(session_token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
