from uuid import uuid4

import pytest
from django.conf import settings
from rest_framework import status

from ledger.transactions.services import credit_increase


@pytest.mark.django_db
class TestTransactionListPagination:
    """Pagination tests for GET /api/transactions/."""

    def test_paginates_results(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: list endpoint returns paginated results with count and navigation."""
        for _ in range(3):
            credit_increase(
                user=user,
                wallet_id=wallet.id,
                data={"amount": 5, "idempotency_key": uuid4()},
            )

        response = authenticated_api_client.get(transaction_list_url, {"page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        result = response.json()["result"]
        assert result["count"] == 3
        assert len(result["results"]) == 2
        assert result["next"] is not None

    def test_rejects_page_size_above_max(self, authenticated_api_client, transaction_list_url):
        """sad path: page_size above MAX_PAGE_SIZE returns 400."""
        max_page_size = settings.REST_FRAMEWORK["MAX_PAGE_SIZE"]

        response = authenticated_api_client.get(
            transaction_list_url,
            {"page_size": max_page_size + 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_uses_default_page_size(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: omitting page_size uses the configured default."""
        default_page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        for _ in range(default_page_size + 1):
            credit_increase(
                user=user,
                wallet_id=wallet.id,
                data={"amount": 5, "idempotency_key": uuid4()},
            )

        response = authenticated_api_client.get(transaction_list_url)

        assert response.status_code == status.HTTP_200_OK
        result = response.json()["result"]
        assert result["count"] == default_page_size + 1
        assert len(result["results"]) == default_page_size

    def test_second_page_returns_remaining(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: second page contains remaining items."""
        for _ in range(3):
            credit_increase(
                user=user,
                wallet_id=wallet.id,
                data={"amount": 5, "idempotency_key": uuid4()},
            )

        response = authenticated_api_client.get(transaction_list_url, {"page_size": 2, "p": 2})

        assert response.status_code == status.HTTP_200_OK
        result = response.json()["result"]
        assert len(result["results"]) == 1
        assert result["previous"] is not None


@pytest.mark.django_db
class TestWalletMyPagination:
    """Pagination tests for GET /api/wallets/my/."""

    def test_paginates_wallets(self, authenticated_api_client, user):
        """happy path: wallet list paginates when page_size is smaller than total."""
        from model_bakery import baker

        from ledger.wallets.models import Wallet

        for currency in [Wallet.Currency.USD, Wallet.Currency.EUR, Wallet.Currency.IRR]:
            baker.make(Wallet, user=user, currency=currency)

        from django.urls import reverse

        url = reverse("api:wallets:wallet-my")
        response = authenticated_api_client.get(url, {"page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        result = response.json()["result"]
        assert result["count"] == 3
        assert len(result["results"]) == 2
