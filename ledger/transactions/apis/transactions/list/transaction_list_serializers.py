from ledger.transactions.apis.wallets.credit_increase.credit_increase_serializers import (
    CreditIncreaseOutputSerializer,
)


class TransactionListOutputSerializer(CreditIncreaseOutputSerializer):
    """Public transaction fields returned by the transaction list API."""

    class Meta(CreditIncreaseOutputSerializer.Meta):
        pass
