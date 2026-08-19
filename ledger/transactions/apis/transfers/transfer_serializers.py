from rest_framework import serializers

from ledger.transactions.apis.wallets.credit_increase.credit_increase_serializers import (
    CreditIncreaseOutputSerializer,
)


class TransferInputSerializer(serializers.Serializer):
    """Input payload for transferring funds between wallets."""

    sender_wallet_id = serializers.IntegerField(
        help_text="Primary key of the wallet to debit.",
    )
    receiver_wallet_id = serializers.IntegerField(
        help_text="Primary key of the wallet to credit.",
    )
    amount = serializers.IntegerField(
        min_value=1,
        help_text="Amount to transfer between the two wallets in whole units.",
    )
    idempotency_key = serializers.UUIDField(
        help_text="Unique key used to safely retry this transfer request.",
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional note describing this transfer.",
    )


class TransferOutputSerializer(CreditIncreaseOutputSerializer):
    """Public transaction fields returned by the transfer API."""

    class Meta(CreditIncreaseOutputSerializer.Meta):
        pass
