"""WebSocket URL routing for notifications."""

from django.urls import path

from ledger.notifications.consumers.user_notification_consumer import (
    UserNotificationConsumer,
)

websocket_urlpatterns = [
    path("ws/notifications/", UserNotificationConsumer.as_asgi()),
]
