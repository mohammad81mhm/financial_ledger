from uuid import uuid4

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def transfer_url() -> str:
    """Return the transfer API URL."""
    from django.urls import reverse

    return reverse("api:transfers:transfer")


@pytest.mark.django_db
class TestTransferApi:
    """Tests for POST /api/transfers/."""

    def test_creates_transfer_successfully(self, authenticated_api_client, transfer_url, wallet, receiver_wallet):
        """happy path: transfer debits sender, credits receiver, returns 201."""
        payload = {
            "sender_wallet_id": wallet.id,
            "receiver_wallet_id": receiver_wallet.id,
            "amount": "100.00",
            "idempotency_key": str(uuid4()),
        }

        response = authenticated_api_client.post(transfer_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()["result"]
        assert result["amount"] == 100
        assert result["sender_wallet"]["balance"] == 900
        assert result["receiver_wallet"]["balance"] == 300

    def test_idempotent_retry_returns_200(self, authenticated_api_client, transfer_url, wallet, receiver_wallet):
        """happy path: duplicate idempotency key returns 200 with original transaction."""
        idempotency_key = str(uuid4())
        payload = {
            "sender_wallet_id": wallet.id,
            "receiver_wallet_id": receiver_wallet.id,
            "amount": "50.00",
            "idempotency_key": idempotency_key,
        }

        first = authenticated_api_client.post(transfer_url, payload, format="json")
        second = authenticated_api_client.post(transfer_url, payload, format="json")

        assert first.status_code == status.HTTP_201_CREATED
        assert second.status_code == status.HTTP_200_OK
        assert first.json()["result"]["id"] == second.json()["result"]["id"]

    def test_rejects_currency_mismatch(self, authenticated_api_client, transfer_url, wallet, wallet_eur):
        """sad path: transfer between wallets of different currencies returns 400."""
        payload = {
            "sender_wallet_id": wallet.id,
            "receiver_wallet_id": wallet_eur.id,
            "amount": "10.00",
            "idempotency_key": str(uuid4()),
        }

        response = authenticated_api_client.post(transfer_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_insufficient_balance(self, authenticated_api_client, transfer_url, wallet, receiver_wallet):
        """sad path: transfer more than sender balance returns 400."""
        payload = {
            "sender_wallet_id": wallet.id,
            "receiver_wallet_id": receiver_wallet.id,
            "amount": "9999.00",
            "idempotency_key": str(uuid4()),
        }

        response = authenticated_api_client.post(transfer_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_self_transfer(self, authenticated_api_client, transfer_url, wallet):
        """sad path: sender and receiver cannot be the same wallet."""
        payload = {
            "sender_wallet_id": wallet.id,
            "receiver_wallet_id": wallet.id,
            "amount": "10.00",
            "idempotency_key": str(uuid4()),
        }

        response = authenticated_api_client.post(transfer_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_requires_authentication(self, transfer_url, wallet, receiver_wallet):
        """sad path: unauthenticated request returns 401."""
        client = APIClient()
        payload = {
            "sender_wallet_id": wallet.id,
            "receiver_wallet_id": receiver_wallet.id,
            "amount": "10.00",
            "idempotency_key": str(uuid4()),
        }

        response = client.post(transfer_url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
