from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Django app configuration for shared core utilities and API plumbing."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ledger.core"
