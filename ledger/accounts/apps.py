from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Django app configuration for user accounts."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ledger.accounts"
