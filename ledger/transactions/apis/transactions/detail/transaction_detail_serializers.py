from ledger.transactions.apis.transactions.list.transaction_list_serializers import (
    TransactionListOutputSerializer,
)


class TransactionDetailOutputSerializer(TransactionListOutputSerializer):
    """Public transaction fields returned by the transaction detail API."""

    class Meta(TransactionListOutputSerializer.Meta):
        pass
