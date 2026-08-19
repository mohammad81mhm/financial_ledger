from uuid import uuid4

import pytest

from ledger.transactions.services import credit_increase, transfer_between_wallets


@pytest.mark.django_db
def test_credit_increase_idempotency_returns_existing_transaction(user, wallet):
    """happy path: repeated credit increase requests return the original transaction."""
    idempotency_key = uuid4()
    data = {
        "amount": 75,
        "idempotency_key": idempotency_key,
    }

    first_entry, first_duplicate = credit_increase(
        user=user,
        wallet_id=wallet.id,
        data=data,
    )
    second_entry, second_duplicate = credit_increase(
        user=user,
        wallet_id=wallet.id,
        data=data,
    )

    wallet.refresh_from_db()

    assert first_duplicate is False
    assert second_duplicate is True
    assert first_entry.id == second_entry.id
    assert wallet.balance == 1075


@pytest.mark.django_db
def test_transfer_idempotency_returns_existing_transaction(user, wallet, receiver_wallet):
    """happy path: repeated transfer requests return the original transaction."""
    idempotency_key = uuid4()
    data = {
        "sender_wallet_id": wallet.id,
        "receiver_wallet_id": receiver_wallet.id,
        "amount": 40,
        "idempotency_key": idempotency_key,
    }

    first_entry, first_duplicate = transfer_between_wallets(
        user=user,
        data=data,
    )
    second_entry, second_duplicate = transfer_between_wallets(
        user=user,
        data=data,
    )

    wallet.refresh_from_db()
    receiver_wallet.refresh_from_db()

    assert first_duplicate is False
    assert second_duplicate is True
    assert first_entry.id == second_entry.id
    assert wallet.balance == 960
    assert receiver_wallet.balance == 240
