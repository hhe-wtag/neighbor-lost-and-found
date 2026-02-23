from fastapi import APIRouter, HTTPException, status, Cookie, Response
from typing import Annotated, Optional

from app.api.v1.deps import AuthServiceDep
from app.schemas.user import UserCreate, UserRead
from app.schemas.session import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(schema: UserCreate, auth: AuthServiceDep):
    result = await auth.register_user(schema)

    return result


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(schema: LoginRequest, auth: AuthServiceDep, response: Response):
    user, session_token, expires_at = await auth.login(
        email=schema.email, password=schema.password
    )

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        expires=expires_at,
    )

    return {"message": "Login successful"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    auth: AuthServiceDep,
    response: Response,
    session_token: Annotated[Optional[str], Cookie()] = None,
):
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    await auth.logout(session_token)
    response.delete_cookie(key="session_token")


@router.get("/me", response_model=UserRead)
async def me(
    auth: AuthServiceDep, session_token: Annotated[Optional[str], Cookie()] = None
):
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return await auth.get_current_user(session_token)
