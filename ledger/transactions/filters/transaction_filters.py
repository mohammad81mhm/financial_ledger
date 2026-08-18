import django_filters

from ledger.transactions.models import TransactionLedger


class TransactionFilter(django_filters.FilterSet):
    """Query filters for transaction list endpoints."""

    transaction_type = django_filters.ChoiceFilter(
        choices=TransactionLedger.TransactionType.choices
    )
    status = django_filters.ChoiceFilter(choices=TransactionLedger.Status.choices)
    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = TransactionLedger
        fields = ["transaction_type", "status"]
