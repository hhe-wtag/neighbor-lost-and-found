from fastapi import APIRouter

from app.api.v1.endpoints import users

api_router = APIRouter(prefix="/v1")

api_router.include_router(users.router)


@api_router.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}
