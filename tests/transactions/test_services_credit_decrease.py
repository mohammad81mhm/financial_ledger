from uuid import uuid4

import pytest

from ledger.core.exceptions import ApplicationError
from ledger.transactions.models import TransactionLedger
from ledger.transactions.services import credit_decrease


@pytest.mark.django_db
def test_credit_decrease_decreases_balance(user, wallet):
    """happy path: credit decrease deducts funds and records a completed withdrawal."""
    data = {
        "amount": 100,
        "idempotency_key": uuid4(),
    }

    ledger_entry, is_duplicate = credit_decrease(
        user=user,
        wallet_id=wallet.id,
        data=data,
    )

    wallet.refresh_from_db()

    assert is_duplicate is False
    assert ledger_entry.transaction_type == TransactionLedger.TransactionType.WITHDRAWAL
    assert ledger_entry.sender_wallet_id == wallet.id
    assert wallet.balance == 900


@pytest.mark.django_db
def test_credit_decrease_rejects_insufficient_balance(user, wallet):
    """sad path: credit decrease fails when the wallet balance is too low."""
    data = {
        "amount": 1500,
        "idempotency_key": uuid4(),
    }

    with pytest.raises(ApplicationError) as exc_info:
        credit_decrease(
            user=user,
            wallet_id=wallet.id,
            data=data,
        )

    wallet.refresh_from_db()

    assert exc_info.value.default_code == "insufficient_balance"
    assert wallet.balance == 1000
