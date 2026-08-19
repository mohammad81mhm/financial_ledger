from django.apps import AppConfig


class WalletsConfig(AppConfig):
    """Django app configuration for user wallets."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ledger.wallets"
