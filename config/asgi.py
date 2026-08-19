import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.local")

django_asgi_app = get_asgi_application()

from config.routing import websocket_urlpatterns  # noqa: E402
from ledger.notifications.middleware.jwt_auth_middleware import (  # noqa: E402
    JWTAuthMiddleware,
)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
