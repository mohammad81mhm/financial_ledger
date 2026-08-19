"""Tests for wallet API endpoints."""

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestWalletDefineApi:
    """Tests for POST /api/wallets/define/."""

    def test_creates_wallet_successfully(
        self, authenticated_api_client, wallet_define_url
    ):
        """happy path: creates a wallet and returns 201 with wallet data."""
        payload = {"currency": "USD", "initial_balance": "50.00"}

        response = authenticated_api_client.post(
            wallet_define_url, payload, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()["result"]
        assert result["currency"] == "USD"
        assert Decimal(result["balance"]) == Decimal("50.00")

    def test_creates_wallet_without_initial_balance(
        self, authenticated_api_client, wallet_define_url
    ):
        """happy path: creates a wallet with zero balance when initial_balance is omitted."""
        payload = {"currency": "EUR"}

        response = authenticated_api_client.post(
            wallet_define_url, payload, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.json()["result"]["balance"]) == Decimal("0.00")

    def test_rejects_duplicate_currency(
        self, authenticated_api_client, wallet_define_url, usd_wallet
    ):
        """sad path: rejects a wallet in a currency the user already has."""
        payload = {"currency": "USD"}

        response = authenticated_api_client.post(
            wallet_define_url, payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_invalid_currency(
        self, authenticated_api_client, wallet_define_url
    ):
        """sad path: rejects an unsupported currency code."""
        payload = {"currency": "GBP"}

        response = authenticated_api_client.post(
            wallet_define_url, payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_negative_initial_balance(
        self, authenticated_api_client, wallet_define_url
    ):
        """sad path: rejects a negative initial balance."""
        payload = {"currency": "USD", "initial_balance": "-10.00"}

        response = authenticated_api_client.post(
            wallet_define_url, payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_requires_authentication(self, wallet_define_url):
        """sad path: rejects unauthenticated requests."""
        client = APIClient()

        response = client.post(
            wallet_define_url, {"currency": "USD"}, format="json"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestWalletMyApi:
    """Tests for GET /api/wallets/my/."""

    def test_returns_user_wallets(
        self, authenticated_api_client, wallet_my_url, usd_wallet, eur_wallet
    ):
        """happy path: returns all wallets for the authenticated user."""
        response = authenticated_api_client.get(wallet_my_url)

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert len(results) == 2

    def test_excludes_other_users_wallets(
        self, authenticated_api_client, wallet_my_url, usd_wallet, other_user
    ):
        """happy path: does not return wallets belonging to another user."""
        from model_bakery import baker
        from ledger.wallets.models import Wallet

        baker.make(Wallet, user=other_user, currency=Wallet.Currency.IRR)

        response = authenticated_api_client.get(wallet_my_url)

        results = response.json()["result"]["results"]
        assert len(results) == 1

    def test_returns_empty_when_no_wallets(
        self, authenticated_api_client, wallet_my_url
    ):
        """happy path: returns empty list when user has no wallets."""
        response = authenticated_api_client.get(wallet_my_url)

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert len(results) == 0

    def test_requires_authentication(self, wallet_my_url):
        """sad path: rejects unauthenticated requests."""
        client = APIClient()

        response = client.get(wallet_my_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
