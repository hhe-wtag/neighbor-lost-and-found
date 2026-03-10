from fastapi import APIRouter

from app.api.v1.endpoints import users, auth, item, item_photo, item_claim

api_router = APIRouter(prefix="/v1")

api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(item.router)
api_router.include_router(item_photo.router)
api_router.include_router(item_claim.router)


@api_router.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}
