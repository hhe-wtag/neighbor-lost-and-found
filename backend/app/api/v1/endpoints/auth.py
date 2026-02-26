from fastapi import APIRouter, status, Cookie, Response
from typing import Annotated, Optional

from app.api.v1.deps import AuthServiceDep
from app.core.exception import UnauthorizedException
from app.schemas.base_response import APIResponse
from app.schemas.user import UserCreate, UserResponse
from app.schemas.session import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


# ------------------------------------------------------------------
# POST /auth/register — register a new user
# ------------------------------------------------------------------
@router.post(
    "/register", response_model=APIResponse[None], status_code=status.HTTP_201_CREATED
)
async def register(schema: UserCreate, auth: AuthServiceDep):
    await auth.register_user(schema)

    return {
        "success": True,
        "data": None,
        "message": "User registered successfully. Please check your email to verify your account.",
    }


# ------------------------------------------------------------------
# POST /auth/login — authenticate user & set session cookie
# ------------------------------------------------------------------
@router.post(
    "/login", response_model=APIResponse[UserResponse], status_code=status.HTTP_200_OK
)
async def login(schema: LoginRequest, auth: AuthServiceDep, response: Response):
    user, session_token, expires_at = await auth.login(
        email=schema.email,
        password=schema.password,
    )

    # Set secure HTTP-only session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        expires=expires_at,
    )

    return {
        "success": True,
        "data": user,
        "message": "Login successful.",
    }


# ------------------------------------------------------------------
# POST /auth/logout — invalidate session & clear cookie
# ------------------------------------------------------------------
@router.post(
    "/logout", response_model=APIResponse[None], status_code=status.HTTP_200_OK
)
async def logout(
    auth: AuthServiceDep,
    response: Response,
    session_token: Annotated[Optional[str], Cookie()] = None,
):
    if not session_token:
        raise UnauthorizedException("Not authenticated")

    await auth.logout(session_token)

    response.delete_cookie(key="session_token")

    return {
        "success": True,
        "data": None,
        "message": "Logout successful.",
    }


# ------------------------------------------------------------------
# GET /auth/me — get currently authenticated user
# ------------------------------------------------------------------
@router.get("/me", response_model=APIResponse[UserResponse])
async def me(
    auth: AuthServiceDep, session_token: Annotated[Optional[str], Cookie()] = None
):
    if not session_token:
        raise UnauthorizedException("Not authenticated")

    user = await auth.get_current_user(session_token)

    return {
        "success": True,
        "data": user,
        "message": "Current user retrieved successfully.",
    }
