"""
Custom application exceptions.

Raise these from services/repositories instead of FastAPI's HTTPException.
The global exception handlers in main.py convert them into the standard
API response format automatically.

Usage:
    raise NotFoundException("User not found")
    raise ConflictException("Email already taken")
    raise ForbiddenException("You can only view your own tickets")
"""

from http import HTTPStatus


class AppException(Exception):
    """Base exception for all application-level errors."""

    status_code: int = 500
    default_message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource does not exist (HTTP 404)."""
    status_code = 404
    default_message = "Resource not found"


class ConflictException(AppException):
    """Resource already exists / duplicate key (HTTP 409)."""
    status_code = 409
    default_message = "Resource already exists"


class BadRequestException(AppException):
    """Invalid input that fails business-rule validation (HTTP 400)."""
    status_code = 400
    default_message = "Bad request"


class UnauthorizedException(AppException):
    """Authentication required or credentials invalid (HTTP 401)."""
    status_code = 401
    default_message = "Authentication required"


class ForbiddenException(AppException):
    """Authenticated but not authorized (HTTP 403)."""
    status_code = 403
    default_message = "Access forbidden"


class ServiceException(AppException):
    """Unexpected error inside a service or repository (HTTP 500)."""
    status_code = 500
    default_message = "Internal server error"

