from decimal import Decimal
from uuid import uuid4

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from ledger.transactions.models import TransactionLedger
from ledger.transactions.services import credit_increase


@pytest.fixture
def api_client(user) -> APIClient:
    """Return an authenticated API client for transaction endpoint tests."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_credit_increase_returns_201_then_200(api_client, user, wallet):
    """happy path: first credit increase creates a transaction and retries return 200."""
    idempotency_key = uuid4()
    payload = {
        "amount": "25.00",
        "idempotency_key": str(idempotency_key),
        "description": "Top up",
    }
    url = f"/api/transactions/wallets/{wallet.id}/credit-increase/"

    first_response = api_client.post(url, payload, format="json")
    second_response = api_client.post(url, payload, format="json")

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_200_OK
    first_result = first_response.json()["result"]
    second_result = second_response.json()["result"]
    assert first_result["id"] == second_result["id"]


@pytest.mark.django_db
def test_credit_increase_requires_authentication(wallet):
    """sad path: credit increase rejects unauthenticated requests."""
    client = APIClient()
    url = f"/api/transactions/wallets/{wallet.id}/credit-increase/"
    response = client.post(
        url,
        {"amount": "10.00", "idempotency_key": str(uuid4())},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_transaction_list_returns_user_transactions(api_client, user, wallet):
    """happy path: transaction list returns transactions for the authenticated user."""
    credit_increase(
        user=user,
        wallet_id=wallet.id,
        data={
            "amount": Decimal("15.00"),
            "idempotency_key": uuid4(),
        },
    )

    response = api_client.get("/api/transactions/")

    assert response.status_code == status.HTTP_200_OK
    transactions = response.json()["result"]["results"]
    assert transactions[0]["transaction_type"] == TransactionLedger.TransactionType.DEPOSIT


@pytest.mark.django_db
def test_transaction_detail_returns_404_for_foreign_transaction(
    api_client, user, other_user, receiver_wallet
):
    """sad path: transaction detail hides transactions that do not belong to the user."""
    ledger_entry, _ = credit_increase(
        user=other_user,
        wallet_id=receiver_wallet.id,
        data={
            "amount": Decimal("10.00"),
            "idempotency_key": uuid4(),
        },
    )

    response = api_client.get(f"/api/transactions/{ledger_entry.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
