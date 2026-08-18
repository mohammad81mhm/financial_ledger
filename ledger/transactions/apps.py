from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    """Django app configuration for wallet transactions."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ledger.transactions"
