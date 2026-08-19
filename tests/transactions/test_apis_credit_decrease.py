from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def credit_decrease_url(wallet) -> str:
    """Return the credit-decrease API URL for the default wallet."""
    return reverse(
        "api:transactions:wallet-credit-decrease",
        kwargs={"wallet_id": wallet.id},
    )


@pytest.mark.django_db
class TestWalletCreditDecreaseApi:
    """Tests for POST /api/transactions/wallets/{wallet_id}/credit-decrease/."""

    def test_returns_201_on_success(self, authenticated_api_client, credit_decrease_url):
        """happy path: credit decrease debits wallet and returns 201."""
        payload = {
            "amount": "100.00",
            "idempotency_key": str(uuid4()),
        }

        response = authenticated_api_client.post(credit_decrease_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()["result"]
        assert result["amount"] == 100
        assert result["sender_wallet"]["balance"] == 900
        assert result["receiver_wallet"] is None

    def test_idempotent_retry_returns_200(self, authenticated_api_client, credit_decrease_url):
        """happy path: duplicate idempotency key returns 200 with original transaction."""
        idempotency_key = str(uuid4())
        payload = {
            "amount": "50.00",
            "idempotency_key": idempotency_key,
        }

        first = authenticated_api_client.post(credit_decrease_url, payload, format="json")
        second = authenticated_api_client.post(credit_decrease_url, payload, format="json")

        assert first.status_code == status.HTTP_201_CREATED
        assert second.status_code == status.HTTP_200_OK
        assert first.json()["result"]["id"] == second.json()["result"]["id"]

    def test_rejects_insufficient_balance(self, authenticated_api_client, credit_decrease_url):
        """sad path: deducting more than balance returns 400."""
        payload = {
            "amount": "9999.00",
            "idempotency_key": str(uuid4()),
        }

        response = authenticated_api_client.post(credit_decrease_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_foreign_wallet(self, authenticated_api_client, receiver_wallet):
        """sad path: credit decrease on another user's wallet returns 404."""
        url = reverse(
            "api:transactions:wallet-credit-decrease",
            kwargs={"wallet_id": receiver_wallet.id},
        )
        payload = {
            "amount": "10.00",
            "idempotency_key": str(uuid4()),
        }

        response = authenticated_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_requires_authentication(self, credit_decrease_url):
        """sad path: unauthenticated request returns 401."""
        client = APIClient()

        response = client.post(
            credit_decrease_url,
            {"amount": "10.00", "idempotency_key": str(uuid4())},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
