from uuid import uuid4

import pytest
from rest_framework.exceptions import ValidationError

from ledger.core.exceptions import ApplicationError
from ledger.transactions.models import TransactionLedger
from ledger.transactions.services import transfer_between_wallets


@pytest.mark.django_db
def test_transfer_between_wallets_updates_both_balances(user, wallet, receiver_wallet):
    """happy path: transfer debits sender and credits receiver atomically."""
    data = {
        "sender_wallet_id": wallet.id,
        "receiver_wallet_id": receiver_wallet.id,
        "amount": 300,
        "idempotency_key": uuid4(),
    }

    ledger_entry, is_duplicate = transfer_between_wallets(
        user=user,
        data=data,
    )

    wallet.refresh_from_db()
    receiver_wallet.refresh_from_db()

    assert is_duplicate is False
    assert ledger_entry.transaction_type == TransactionLedger.TransactionType.TRANSFER
    assert wallet.balance == 700
    assert receiver_wallet.balance == 500


@pytest.mark.django_db
def test_transfer_between_wallets_rejects_currency_mismatch(user, wallet, wallet_eur):
    """sad path: transfer fails when sender and receiver currencies differ."""
    data = {
        "sender_wallet_id": wallet.id,
        "receiver_wallet_id": wallet_eur.id,
        "amount": 50,
        "idempotency_key": uuid4(),
    }

    with pytest.raises(ApplicationError) as exc_info:
        transfer_between_wallets(
            user=user,
            data=data,
        )

    assert exc_info.value.default_code == "currency_mismatch"


@pytest.mark.django_db
def test_transfer_between_wallets_rejects_self_transfer(user, wallet):
    """sad path: transfer fails when sender and receiver are the same wallet."""
    data = {
        "sender_wallet_id": wallet.id,
        "receiver_wallet_id": wallet.id,
        "amount": 50,
        "idempotency_key": uuid4(),
    }

    with pytest.raises(ValidationError):
        transfer_between_wallets(
            user=user,
            data=data,
        )


@pytest.mark.django_db
def test_transfer_between_wallets_consumes_remaining_limit(user, wallet, receiver_wallet):
    """happy path: successful transfer decreases the sender remaining limit."""
    data = {
        "sender_wallet_id": wallet.id,
        "receiver_wallet_id": receiver_wallet.id,
        "amount": 50,
        "idempotency_key": uuid4(),
    }

    transfer_between_wallets(user=user, data=data)

    wallet.refresh_from_db()
    assert wallet.remaining_limit == 9_950


@pytest.mark.django_db
def test_transfer_between_wallets_rejects_insufficient_remaining_limit(
    user,
    wallet,
    receiver_wallet,
):
    """sad path: transfer fails when amount exceeds the sender remaining limit."""
    wallet.remaining_limit = 40
    wallet.save(update_fields=["remaining_limit"])

    data = {
        "sender_wallet_id": wallet.id,
        "receiver_wallet_id": receiver_wallet.id,
        "amount": 50,
        "idempotency_key": uuid4(),
    }

    with pytest.raises(ValidationError):
        transfer_between_wallets(user=user, data=data)

    wallet.refresh_from_db()
    receiver_wallet.refresh_from_db()
    assert wallet.balance == 1000
    assert wallet.remaining_limit == 40
    assert receiver_wallet.balance == 200
