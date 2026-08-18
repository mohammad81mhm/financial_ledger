"""Root ASGI routing for HTTP and WebSocket protocols."""

from ledger.notifications.routing.notification_routing import websocket_urlpatterns

__all__ = ["websocket_urlpatterns"]
