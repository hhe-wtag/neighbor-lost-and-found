from datetime import datetime, timedelta, timezone

from app.core.exception import ConflictException, UnauthorizedException
from app.core.security import verify_password, generate_session_token, get_password_hash
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.session import SessionRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository):
        self.user_repo = user_repo
        self.session_repo = session_repo

    # ------------------------------------------------------------------
    # User registration
    # ------------------------------------------------------------------
    async def register_user(self, schema: UserCreate) -> None:
        existing_user = await self.user_repo.get_by_email(email=schema.email)

        if existing_user:
            raise ConflictException("Email already registered")

        hashed_password = get_password_hash(schema.password)

        await self.user_repo.create(
            schema,
            hashed_password=hashed_password,
        )

    # ------------------------------------------------------------------
    # Authenticate user credentials
    # ------------------------------------------------------------------
    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email=email)

        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")

        return user

    # ------------------------------------------------------------------
    # Login — create session & return token
    # ------------------------------------------------------------------
    async def login(self, email: str, password: str) -> tuple[User, str, datetime]:
        user = await self.authenticate_user(email, password)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        session_token = generate_session_token(user)

        await self.session_repo.create_session(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
        )

        return user, session_token, expires_at

    # ------------------------------------------------------------------
    # Logout — invalidate session
    # ------------------------------------------------------------------
    async def logout(self, session_token: str) -> None:
        session = await self.session_repo.get_by_token(session_token)

        if not session:
            raise UnauthorizedException("Invalid session token")

        await self.session_repo.invalidate(session)

    # ------------------------------------------------------------------
    # Get current authenticated user
    # ------------------------------------------------------------------
    async def get_current_user(self, session_token: str) -> User:
        session = await self.session_repo.get_by_token(session_token)

        if not session:
            raise UnauthorizedException("Invalid session token")

        if not await self.session_repo.is_valid(session):
            await self.session_repo.invalidate(session)
            raise UnauthorizedException("Session expired")

        user = await self.user_repo.get_by_id(session.user_id)

        if not user:
            raise UnauthorizedException("User not found")

        return user
