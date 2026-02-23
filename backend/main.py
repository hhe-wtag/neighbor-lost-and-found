import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.api import api_router as api_v1_router
from app.core.database import engine
from app.middleware.logger import LoggingMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

app.include_router(api_v1_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Application is running!"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
