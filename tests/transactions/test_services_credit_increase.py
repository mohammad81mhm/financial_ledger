from uuid import uuid4

import pytest
from rest_framework.exceptions import NotFound, ValidationError

from ledger.transactions.models import TransactionLedger
from ledger.transactions.services import credit_increase


@pytest.mark.django_db
def test_credit_increase_increases_balance(user, wallet):
    """happy path: credit increase adds funds and records a completed deposit."""
    idempotency_key = uuid4()
    data = {
        "amount": 250,
        "idempotency_key": idempotency_key,
        "description": "Payroll deposit",
    }

    ledger_entry, is_duplicate = credit_increase(
        user=user,
        wallet_id=wallet.id,
        data=data,
    )

    wallet.refresh_from_db()

    assert is_duplicate is False
    assert ledger_entry.transaction_type == TransactionLedger.TransactionType.DEPOSIT
    assert ledger_entry.status == TransactionLedger.Status.COMPLETED
    assert ledger_entry.receiver_wallet_id == wallet.id
    assert ledger_entry.sender_wallet is None
    assert wallet.balance == 1250


@pytest.mark.django_db
def test_credit_increase_rejects_foreign_wallet(user, receiver_wallet):
    """sad path: credit increase fails when the wallet belongs to another user."""
    data = {
        "amount": 10,
        "idempotency_key": uuid4(),
    }

    with pytest.raises(NotFound):
        credit_increase(
            user=user,
            wallet_id=receiver_wallet.id,
            data=data,
        )


@pytest.mark.django_db
def test_credit_increase_rejects_zero_amount(user, wallet):
    """sad path: credit increase rejects a zero amount."""
    data = {
        "amount": 0,
        "idempotency_key": uuid4(),
    }

    with pytest.raises(ValidationError):
        credit_increase(
            user=user,
            wallet_id=wallet.id,
            data=data,
        )
