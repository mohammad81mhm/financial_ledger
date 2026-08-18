from ledger.transactions.apis.wallets.credit_increase.credit_increase_serializers import (
    CreditIncreaseInputSerializer,
    CreditIncreaseOutputSerializer,
)


class CreditDecreaseInputSerializer(CreditIncreaseInputSerializer):
    """Input payload for debiting funds from a wallet."""


class CreditDecreaseOutputSerializer(CreditIncreaseOutputSerializer):
    """Public transaction fields returned by the credit-decrease API."""

    class Meta(CreditIncreaseOutputSerializer.Meta):
        pass
