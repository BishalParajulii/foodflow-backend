"""Google ID-token verification (Gmail login).

Flow: the client (web/mobile) signs the user in with Google Identity Services,
obtains an ID token, and POSTs it to ``/api/v1/auth/google/``. We verify the
token signature + audience server-side and map it to a local user.
"""

from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import serializers


def verify_google_id_token(token: str) -> dict:
    """Verify a Google ID token and return its claims.

    Raises:
        serializers.ValidationError: if Google login is unconfigured or the
            token is invalid/expired/for another audience.
    """
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    if not client_id:
        raise serializers.ValidationError(
            {"detail": "Google login is not configured (GOOGLE_CLIENT_ID is empty)."}
        )
    try:
        return google_id_token.verify_oauth2_token(
            token, google_requests.Request(), client_id, clock_skew_in_seconds=10
        )
    except ValueError as exc:
        raise serializers.ValidationError({"id_token": f"Invalid Google token: {exc}"})
