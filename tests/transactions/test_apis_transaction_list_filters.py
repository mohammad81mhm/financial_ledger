from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone
from rest_framework import status

from ledger.transactions.models import TransactionLedger
from ledger.transactions.services import credit_increase, transfer_between_wallets


@pytest.mark.django_db
class TestTransactionListFilters:
    """Advanced filter tests for GET /api/transactions/."""

    def test_filters_by_transaction_type(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: transaction_type filter returns only matching rows."""
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 10, "idempotency_key": uuid4()},
        )

        response = authenticated_api_client.get(
            transaction_list_url,
            {"transaction_type": TransactionLedger.TransactionType.DEPOSIT},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert len(results) == 1
        assert results[0]["transaction_type"] == TransactionLedger.TransactionType.DEPOSIT

    def test_filters_by_status(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: status filter returns only completed transactions."""
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 10, "idempotency_key": uuid4()},
        )

        response = authenticated_api_client.get(
            transaction_list_url,
            {"status": TransactionLedger.Status.COMPLETED},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert len(results) == 1
        assert results[0]["status"] == TransactionLedger.Status.COMPLETED

    def test_filters_by_currency(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: currency filter returns only matching currency rows."""
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 10, "idempotency_key": uuid4()},
        )

        response = authenticated_api_client.get(
            transaction_list_url,
            {"currency": wallet.currency},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert len(results) == 1
        assert results[0]["currency"] == wallet.currency

    def test_filters_by_wallet_id(
        self,
        authenticated_api_client,
        transaction_list_url,
        user,
        wallet,
        receiver_wallet,
    ):
        """happy path: wallet_id filter scopes to sender or receiver wallet."""
        transfer_between_wallets(
            user=user,
            data={
                "sender_wallet_id": wallet.id,
                "receiver_wallet_id": receiver_wallet.id,
                "amount": 50,
                "idempotency_key": uuid4(),
            },
        )

        response = authenticated_api_client.get(
            transaction_list_url,
            {"wallet_id": wallet.id},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert len(results) == 1
        assert results[0]["sender_wallet"]["id"] == wallet.id

    def test_rejects_foreign_wallet_id(self, authenticated_api_client, transaction_list_url, receiver_wallet):
        """sad path: wallet_id filter returns 404 for another user's wallet."""
        response = authenticated_api_client.get(
            transaction_list_url,
            {"wallet_id": receiver_wallet.id},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filters_by_amount_range(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: min_amount and max_amount filter by transaction amount."""
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 25, "idempotency_key": uuid4()},
        )
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 100, "idempotency_key": uuid4()},
        )

        response = authenticated_api_client.get(
            transaction_list_url,
            {"min_amount": 30, "max_amount": 120},
        )

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert len(results) == 1
        assert results[0]["amount"] == 100

    def test_filters_by_from_date_and_to_date(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: from_date and to_date filter by created_at date."""
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 10, "idempotency_key": uuid4()},
        )
        ledger_entry = TransactionLedger.objects.get()
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        TransactionLedger.objects.filter(pk=ledger_entry.pk).update(
            created_at=timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
        )

        in_range = authenticated_api_client.get(
            transaction_list_url,
            {"from_date": yesterday.isoformat(), "to_date": today.isoformat()},
        )
        out_of_range = authenticated_api_client.get(
            transaction_list_url,
            {"from_date": tomorrow.isoformat()},
        )

        assert in_range.status_code == status.HTTP_200_OK
        assert len(in_range.json()["result"]["results"]) == 1
        assert out_of_range.status_code == status.HTTP_200_OK
        assert len(out_of_range.json()["result"]["results"]) == 0

    def test_rejects_invalid_date_range(self, authenticated_api_client, transaction_list_url):
        """sad path: from_date after to_date returns 400."""
        response = authenticated_api_client.get(
            transaction_list_url,
            {"from_date": "2026-08-20", "to_date": "2026-08-01"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_invalid_amount_range(self, authenticated_api_client, transaction_list_url):
        """sad path: min_amount greater than max_amount returns 400."""
        response = authenticated_api_client.get(
            transaction_list_url,
            {"min_amount": 500, "max_amount": 100},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_newest_first(self, authenticated_api_client, transaction_list_url, user, wallet):
        """happy path: results are ordered by created_at descending."""
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 10, "idempotency_key": uuid4()},
        )
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data={"amount": 20, "idempotency_key": uuid4()},
        )

        entries = list(TransactionLedger.objects.order_by("created_at"))
        older, newer = entries[0], entries[1]
        TransactionLedger.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=1))
        TransactionLedger.objects.filter(pk=newer.pk).update(created_at=timezone.now())

        response = authenticated_api_client.get(transaction_list_url)

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["result"]["results"]
        assert results[0]["id"] == str(newer.id)
        assert results[1]["id"] == str(older.id)
