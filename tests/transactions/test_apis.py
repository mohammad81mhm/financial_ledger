from uuid import uuid4

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from ledger.transactions.models import TransactionLedger
from ledger.transactions.services import credit_increase


@pytest.mark.django_db
class TestWalletCreditIncreaseApi:
    """Tests for POST /api/transactions/wallets/{wallet_id}/credit-increase/."""

    def test_returns_201_then_200(
        self,
        authenticated_api_client,
        credit_increase_url,
    ):
        """happy path: first credit increase creates a transaction and retries return 200."""
        idempotency_key = uuid4()
        payload = {
            "amount": "25.00",
            "idempotency_key": str(idempotency_key),
            "description": "Top up",
        }

        first_response = authenticated_api_client.post(credit_increase_url, payload, format="json")
        second_response = authenticated_api_client.post(credit_increase_url, payload, format="json")

        assert first_response.status_code == status.HTTP_201_CREATED
        assert second_response.status_code == status.HTTP_200_OK
        first_result = first_response.json()["result"]
        second_result = second_response.json()["result"]
        assert first_result["id"] == second_result["id"]
        assert first_result["sender_wallet"] is None
        assert first_result["receiver_wallet"]["balance"] == 1025
        assert second_result["receiver_wallet"]["balance"] == 1025

    def test_requires_authentication(self, credit_increase_url):
        """sad path: credit increase rejects unauthenticated requests."""
        client = APIClient()
        response = client.post(
            credit_increase_url,
            {"amount": "10.00", "idempotency_key": str(uuid4())},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTransactionListApi:
    """Tests for GET /api/transactions/."""

    def test_returns_user_transactions(
        self,
        authenticated_api_client,
        transaction_list_url,
        user,
        wallet,
    ):
        """happy path: transaction list returns transactions for the authenticated user."""
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={
                "amount": 15,
                "idempotency_key": uuid4(),
            },
        )

        response = authenticated_api_client.get(transaction_list_url)

        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()["result"]["results"]
        assert transactions[0]["transaction_type"] == TransactionLedger.TransactionType.DEPOSIT


@pytest.mark.django_db
class TestTransactionDetailApi:
    """Tests for GET /api/transactions/{transaction_id}/."""

    def test_returns_404_for_foreign_transaction(
        self,
        authenticated_api_client,
        transaction_detail_url,
        other_user,
        receiver_wallet,
    ):
        """sad path: transaction detail hides transactions that do not belong to the user."""
        ledger_entry, _ = credit_increase(
            user=other_user,
            wallet_id=receiver_wallet.id,
            data={
                "amount": 10,
                "idempotency_key": uuid4(),
            },
        )

        response = authenticated_api_client.get(
            transaction_detail_url(transaction_id=ledger_entry.id),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
