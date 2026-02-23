import hashlib
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext

from app.models.user import User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_session_token(user: User) -> str:
    raw = f"{uuid.uuid4()}-{user.id}-{datetime.now(timezone.utc).timestamp()}"
    return hashlib.sha256(raw.encode()).hexdigest()
