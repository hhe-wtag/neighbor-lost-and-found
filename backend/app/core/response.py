from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Optional[Any] = None,
    message: str = "Success",
    status_code: int = 200,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "message": message,
        },
    )


def error_response(
    message: Any,
    status_code: int = 500,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "message": message,
        },
    )
