import django_filters
from django.db.models import Q

from ledger.transactions.models import TransactionLedger
from ledger.wallets.models import Wallet


class TransactionFilter(django_filters.FilterSet):
    """Query filters for transaction list endpoints."""

    transaction_type = django_filters.ChoiceFilter(choices=TransactionLedger.TransactionType.choices)
    status = django_filters.ChoiceFilter(choices=TransactionLedger.Status.choices)
    from_date = django_filters.DateFilter(method="filter_from_date")
    to_date = django_filters.DateFilter(method="filter_to_date")
    wallet_id = django_filters.NumberFilter(method="filter_wallet_id")
    currency = django_filters.ChoiceFilter(choices=Wallet.Currency.choices)
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = TransactionLedger
        fields = [
            "transaction_type",
            "status",
            "from_date",
            "to_date",
            "wallet_id",
            "currency",
            "min_amount",
            "max_amount",
        ]

    def filter_from_date(self, queryset, name, value):
        """Filter transactions on or after the given date."""
        return queryset.filter(created_at__date__gte=value)

    def filter_to_date(self, queryset, name, value):
        """Filter transactions on or before the given date."""
        return queryset.filter(created_at__date__lte=value)

    def filter_wallet_id(self, queryset, name, value):
        """Filter transactions where the wallet is sender or receiver."""
        return queryset.filter(Q(sender_wallet_id=value) | Q(receiver_wallet_id=value))
