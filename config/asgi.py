"""ASGI entrypoint — Channels-ready (no consumers/routing yet)."""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django_asgi_app = get_asgi_application()

# WebSocket routing will be added in a later phase, e.g.:
#   from channels.auth import AuthMiddlewareStack
#   from channels.security.websocket import AllowedHostsOriginValidator
#   websocket_urlpatterns = [...]
#   "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(
#       URLRouter(websocket_urlpatterns)
#   )),
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # "websocket": ... (not implemented in scaffolding phase)
    }
)
