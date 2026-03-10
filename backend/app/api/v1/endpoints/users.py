from fastapi import APIRouter
from typing import List

from app.core.exception import NotFoundException, BadRequestException
from app.schemas.base_response import APIResponse
from app.schemas.user import UserResponse, UserUpdate
from app.api.v1.deps import UserRepoDep

router = APIRouter(prefix="/users", tags=["Users"])


# ------------------------------------------------------------------
# GET /users — get all users (useful for admin moderation)
# ------------------------------------------------------------------
@router.get("/", response_model=APIResponse[List[UserResponse]])
async def get_all_users(repo: UserRepoDep, offset: int = 0, limit: int = 100):
    users = await repo.get_all(offset=offset, limit=limit)

    return {
        "success": True,
        "data": users,
        "message": "Users retrieved successfully.",
    }


# ------------------------------------------------------------------
# GET /users/{user_id} — get single user
# ------------------------------------------------------------------
@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(user_id: int, repo: UserRepoDep):
    user = await repo.get_by_id(id=user_id)
    if not user:
        raise NotFoundException("User not found")

    return {
        "success": True,
        "data": user,
        "message": "User retrieved successfully.",
    }


# ------------------------------------------------------------------
#  PATCH /users/{user_id} — update user data
# ------------------------------------------------------------------
@router.patch("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(user_id: int, user_data: UserUpdate, repo: UserRepoDep):
    user = await repo.get_by_id(id=user_id)
    if not user:
        raise NotFoundException("User not found")

    if user_data.email and user_data.email != user.email:
        existing_user = await repo.get_by_email(email=user_data.email)
        if existing_user:
            raise BadRequestException("Email already registered")

    updated_user = await repo.update(user, user_data)

    return {
        "success": True,
        "data": updated_user,
        "message": "User updated successfully.",
    }


# ------------------------------------------------------------------
#  DELETE /users/{user_id} — delete user
# ------------------------------------------------------------------
@router.delete("/{user_id}", response_model=APIResponse[None])
async def delete_user(user_id: int, repo: UserRepoDep):
    user = await repo.get_by_id(id=user_id)
    if not user:
        raise NotFoundException("User not found")

    await repo.delete(user)

    return {
        "success": True,
        "data": None,
        "message": "User deleted successfully.",
    }
