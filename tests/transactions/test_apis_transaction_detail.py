"""Tests for GET /api/transactions/{transaction_id}/ (TransactionDetailApi)."""

from decimal import Decimal
from uuid import uuid4

import pytest
from rest_framework import status

from ledger.transactions.models import TransactionLedger
from ledger.transactions.services import credit_increase


@pytest.mark.django_db
class TestTransactionDetailApi:
    """Tests for GET /api/transactions/{transaction_id}/."""

    def test_returns_own_transaction(
        self, authenticated_api_client, transaction_detail_url, user, wallet
    ):
        """happy path: user retrieves their own transaction details."""
        ledger_entry, _ = credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={
                "amount": Decimal("50.00"),
                "idempotency_key": uuid4(),
            },
        )

        response = authenticated_api_client.get(
            transaction_detail_url(transaction_id=ledger_entry.id),
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()["result"]
        assert result["id"] == str(ledger_entry.id)
        assert result["transaction_type"] == TransactionLedger.TransactionType.DEPOSIT
        assert Decimal(result["amount"]) == Decimal("50.00")

    def test_returns_404_for_nonexistent_transaction(
        self, authenticated_api_client, transaction_detail_url
    ):
        """sad path: nonexistent transaction ID returns 404."""
        response = authenticated_api_client.get(
            transaction_detail_url(transaction_id=uuid4()),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
