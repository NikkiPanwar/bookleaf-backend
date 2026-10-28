"""
Standard API response envelope.

Every endpoint returns one of:

Success:
    {
        "success": true,
        "message": "Books fetched successfully",
        "data": { ... }
    }

Error (via exception handler):
    {
        "success": false,
        "message": "User not found",
        "data": null
    }
"""

from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None


def success_response(data: Any = None, message: str = "Success") -> dict:
    """Build a standard success response dict."""
    return ApiResponse(success=True, message=message, data=data).model_dump()


def error_response(message: str = "An error occurred", data: Any = None) -> dict:
    """Build a standard error response dict."""
    return ApiResponse(success=False, message=message, data=data).model_dump()

