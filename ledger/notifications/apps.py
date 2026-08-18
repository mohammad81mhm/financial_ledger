from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Django app configuration for WebSocket notifications."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ledger.notifications"
