from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
