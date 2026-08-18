from decimal import Decimal
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
        "amount": Decimal("300.00"),
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
    assert wallet.balance == Decimal("700.00")
    assert receiver_wallet.balance == Decimal("500.00")


@pytest.mark.django_db
def test_transfer_between_wallets_rejects_currency_mismatch(user, wallet, wallet_eur):
    """sad path: transfer fails when sender and receiver currencies differ."""
    data = {
        "sender_wallet_id": wallet.id,
        "receiver_wallet_id": wallet_eur.id,
        "amount": Decimal("50.00"),
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
        "amount": Decimal("50.00"),
        "idempotency_key": uuid4(),
    }

    with pytest.raises(ValidationError):
        transfer_between_wallets(
            user=user,
            data=data,
        )
