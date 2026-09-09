"""Universal API response envelope (company blueprint contract).

Success: {"success": true, "message": ..., "data": ...}
Error:   {"success": false, "error": {"code": ..., "message": ..., "details": ...}}
"""

from rest_framework.response import Response


def success_response(data=None, message="Operation successful.", status_code=200):
    """Build an enveloped success response."""
    return Response(
        {"success": True, "message": message, "data": data}, status=status_code
    )


def error_response(
    message="Request failed.", *, code="error", details=None, status_code=400
):
    """Build an enveloped error response (for non-DRF exception paths)."""
    return Response(
        {
            "success": False,
            "error": {"code": code, "message": message, "details": details},
        },
        status=status_code,
    )
