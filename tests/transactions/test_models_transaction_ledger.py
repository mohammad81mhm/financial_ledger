from uuid import uuid4

import pytest

from ledger.transactions.models import ImmutableTransactionError
from ledger.transactions.services import credit_increase


@pytest.mark.django_db
def test_transaction_ledger_rejects_updates(user, wallet):
    """sad path: existing ledger rows cannot be mutated via save()."""
    ledger_entry, _ = credit_increase(
        user=user,
        wallet_id=wallet.id,
        data={"amount": 50, "idempotency_key": uuid4()},
    )

    ledger_entry.amount = 999

    with pytest.raises(ImmutableTransactionError, match="cannot be updated"):
        ledger_entry.save()

    ledger_entry.refresh_from_db()
    assert ledger_entry.amount == 50
