"""Global exception handler: wraps all DRF errors in the error envelope."""

from django.db import IntegrityError
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _error_code(exc) -> str:
    if isinstance(exc, ValidationError):
        return "validation_error"
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return "authentication_error"
    if isinstance(exc, PermissionDenied):
        return "permission_denied"
    if isinstance(exc, NotFound):
        return "not_found"
    if isinstance(exc, Throttled):
        return "throttled"
    return getattr(exc, "default_code", None) or "error"


def custom_exception_handler(exc, context):
    """Wrap DRF errors as {"success": False, "error": {...}}. Pass through 500s."""
    if isinstance(exc, IntegrityError):
        detail = (str(exc).splitlines() or ["Database integrity error."])[0]
        return Response(
            {
                "success": False,
                "error": {
                    "code": "integrity_error",
                    "message": "Database integrity error.",
                    "details": {"detail": detail},
                },
            },
            status=400,
        )
    response = exception_handler(exc, context)
    if response is None:
        return None
    data = response.data
    if isinstance(data, dict) and "success" in data:
        return response  # already enveloped
    if isinstance(exc, ValidationError):
        message, details = "Invalid input.", data
    elif isinstance(data, dict) and isinstance(data.get("detail"), str):
        message, details = data["detail"], data
    else:
        message, details = "Request failed.", data
    response.data = {
        "success": False,
        "error": {"code": _error_code(exc), "message": message, "details": details},
    }
    return response
