from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Django app configuration for registration and login."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ledger.authentication"
