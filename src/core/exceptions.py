from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


class AppException(Exception):
    """Base application exception mapped to an HTTP response."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(AppException):
    """Raised when a request conflicts with current persisted state."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class ForbiddenError(AppException):
    """Raised when a user is authenticated but not allowed to perform an action."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for predictable API errors."""

    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(_: Request, __: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Database integrity constraint violated"},
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
