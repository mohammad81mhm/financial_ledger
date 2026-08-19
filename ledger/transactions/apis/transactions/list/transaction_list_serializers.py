from django.conf import settings
from rest_framework import serializers

from ledger.transactions.apis.wallets.credit_increase.credit_increase_serializers import (
    CreditIncreaseOutputSerializer,
)
from ledger.transactions.models import TransactionLedger
from ledger.wallets.models import Wallet

_MAX_PAGE_SIZE = settings.REST_FRAMEWORK["MAX_PAGE_SIZE"]


class TransactionListInputSerializer(serializers.Serializer):
    """Query parameters for listing transactions."""

    p = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="Page number for pagination. Used together with page_size.",
    )
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=_MAX_PAGE_SIZE,
        help_text=(
            f"Number of items per page. Maximum allowed value is {_MAX_PAGE_SIZE}."
        ),
    )
    from_date = serializers.DateField(
        required=False,
        help_text="Include transactions with created_at on or after this date.",
    )
    to_date = serializers.DateField(
        required=False,
        help_text="Include transactions with created_at on or before this date.",
    )
    transaction_type = serializers.ChoiceField(
        required=False,
        choices=TransactionLedger.TransactionType.choices,
        help_text=(
            "Filter by transaction type: DEPOSIT, WITHDRAWAL, or TRANSFER."
        ),
    )
    status = serializers.ChoiceField(
        required=False,
        choices=TransactionLedger.Status.choices,
        help_text="Filter by status: PENDING, COMPLETED, or FAILED.",
    )
    wallet_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text=(
            "Scope results to one owned wallet. Returns 404 when the wallet "
            "does not belong to the authenticated user."
        ),
    )
    currency = serializers.ChoiceField(
        required=False,
        choices=Wallet.Currency.choices,
        help_text="Filter by transaction currency: USD, EUR, or IRR.",
    )
    min_amount = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="Minimum transaction amount in whole units (inclusive).",
    )
    max_amount = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text="Maximum transaction amount in whole units (inclusive).",
    )

    def validate(self, attrs: dict) -> dict:
        """Validate cross-field date and amount ranges."""
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError(
                {"from_date": "from_date must be on or before to_date."}
            )

        min_amount = attrs.get("min_amount")
        max_amount = attrs.get("max_amount")
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise serializers.ValidationError(
                {"min_amount": "min_amount must be less than or equal to max_amount."}
            )

        return attrs


class TransactionListOutputSerializer(CreditIncreaseOutputSerializer):
    """Public transaction fields returned by the transaction list API."""

    class Meta(CreditIncreaseOutputSerializer.Meta):
        pass
