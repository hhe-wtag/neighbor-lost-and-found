import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware


from app.api.v1.api import api_router as api_v1_router
from app.core.database import engine
from app.core.exception import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
)
from app.middleware.logger import LoggingMiddleware
from app.api.v1.deps import cookie_scheme  # noqa


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"withCredentials": True})

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

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
