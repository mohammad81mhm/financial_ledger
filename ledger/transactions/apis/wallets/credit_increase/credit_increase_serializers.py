from decimal import Decimal

from rest_framework import serializers

from ledger.transactions.models import TransactionLedger
from ledger.wallets.models import Wallet


class WalletNestedOutputSerializer(serializers.ModelSerializer):
    """Nested wallet fields included on transaction responses."""

    class Meta:
        model = Wallet
        fields = ["id", "currency", "balance"]
        extra_kwargs = {
            "id": {"help_text": "Primary key of the wallet."},
            "currency": {"help_text": "Currency code for this wallet."},
            "balance": {
                "help_text": "Current wallet balance in the selected currency."
            },
        }


class CreditIncreaseInputSerializer(serializers.Serializer):
    """Input payload for crediting funds into a wallet."""

    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=Decimal("0.01"),
        help_text="Amount to deposit into the wallet.",
    )
    idempotency_key = serializers.UUIDField(
        help_text="Unique key used to safely retry this deposit request.",
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional note describing this deposit.",
    )


class CreditIncreaseOutputSerializer(serializers.ModelSerializer):
    """Public transaction fields returned by the credit-increase API."""

    sender_wallet = WalletNestedOutputSerializer(
        read_only=True,
        allow_null=True,
        help_text="Wallet debited for withdrawals and transfers.",
    )
    receiver_wallet = WalletNestedOutputSerializer(
        read_only=True,
        allow_null=True,
        help_text="Wallet credited for deposits and transfers.",
    )

    class Meta:
        model = TransactionLedger
        fields = [
            "id",
            "idempotency_key",
            "transaction_type",
            "status",
            "amount",
            "currency",
            "sender_wallet",
            "receiver_wallet",
            "description",
            "created_at",
        ]
        extra_kwargs = {
            "id": {"help_text": "Unique identifier for this transaction."},
            "idempotency_key": {
                "help_text": "Client-supplied key that guarantees at-most-once processing."
            },
            "transaction_type": {
                "help_text": "Kind of wallet movement: deposit, withdrawal, or transfer."
            },
            "status": {"help_text": "Processing status of this transaction."},
            "amount": {"help_text": "Transaction amount in the wallet currency."},
            "currency": {"help_text": "Currency code for this transaction."},
            "description": {"help_text": "Optional note describing this transaction."},
            "created_at": {
                "help_text": "Date and time when this transaction was recorded."
            },
        }
