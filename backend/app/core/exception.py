from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.response import error_response


class AppException(Exception):
    """Base exception for all application errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class BadRequestException(AppException):
    """
    Exception raised when an invalid request is made.
    Status code: 400
    """

    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedException(AppException):
    """
    Raised when user is not authorized.
    Status code: 401
    """

    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(AppException):
    """
    Raised when a user is forbidden to perform the requested action.
    Status Code: 403
    """

    status_code = status.HTTP_403_FORBIDDEN


class NotFoundException(AppException):
    """
    Raised when a requested item is not found.
    Status Code: 404
    """

    status_code = status.HTTP_404_NOT_FOUND


class ConflictException(AppException):
    """
    Raised when a requested item already exists.
    Status Code: 409
    """

    status_code = status.HTTP_409_CONFLICT


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return error_response(
        message=exc.detail,
        status_code=exc.status_code,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    formatted_errors = {}

    for error in exc.errors():
        field = error["loc"][-1]
        formatted_errors.setdefault(field, []).append(error["msg"])

    return error_response(
        message=formatted_errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
