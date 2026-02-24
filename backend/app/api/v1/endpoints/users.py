from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.user import UserResponse, UserUpdate
from app.api.v1.deps import UserRepoDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users(repo: UserRepoDep, offset: int = 0, limit: int = 100):
    return await repo.get_all(offset=offset, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, repo: UserRepoDep):
    user = await repo.get_by_id(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, repo: UserRepoDep):
    user = await repo.get_by_id(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_data.email is not None and user_data.email != user.email:
        existing_user = await repo.get_by_email(email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    return await repo.update(user, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, repo: UserRepoDep):
    user = await repo.get_by_id(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await repo.delete(user)
