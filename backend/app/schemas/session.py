from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    user_id: int
    session_token: str
    expires_at: datetime


class SessionUpdate(BaseModel):
    expires_at: datetime | None = None


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_token: str
    user_id: int
    expires_at: datetime
    created_at: datetime


class SessionToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionTokenData(BaseModel):
    user_id: int | None = None

    def get_id(self) -> int | None:
        return int(self.user_id) if self.user_id else None


class LoginRequest(BaseModel):
    email: str
    password: str
