from rest_framework import serializers

from ledger.wallets.models import Wallet


class WalletDefineInputSerializer(serializers.Serializer):
    """Input payload for creating a wallet."""

    currency = serializers.ChoiceField(
        choices=Wallet.Currency.choices,
        help_text="Currency code for the new wallet, such as USD, EUR, or IRR.",
    )
    initial_balance = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        help_text="Starting balance for the wallet in whole units. Defaults to zero.",
    )


class WalletOutputSerializer(serializers.ModelSerializer):
    """Public wallet fields returned by APIs."""

    class Meta:
        model = Wallet
        fields = ["id", "currency", "balance"]
        extra_kwargs = {
            "id": {"help_text": "Primary key of the wallet."},
            "currency": {"help_text": "Currency code for this wallet."},
            "balance": {"help_text": "Current wallet balance in the selected currency."},
        }
