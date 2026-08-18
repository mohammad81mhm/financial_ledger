from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import uuid4

import pytest

from ledger.core.exceptions import ApplicationError
from ledger.transactions.services import credit_decrease


@pytest.mark.django_db(transaction=True)
def test_concurrent_credit_decreases_prevent_double_spending(user, wallet):
    """happy path: concurrent credit decreases serialize and prevent double spending."""
    barrier_errors: list[Exception] = []

    def attempt_credit_decrease() -> None:
        try:
            credit_decrease(
                user=user,
                wallet_id=wallet.id,
                data={
                    "amount": Decimal("600.00"),
                    "idempotency_key": uuid4(),
                },
            )
        except ApplicationError as exc:
            barrier_errors.append(exc)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(attempt_credit_decrease) for _ in range(2)]
        for future in futures:
            future.result()

    wallet.refresh_from_db()

    assert len(barrier_errors) == 1
    assert wallet.balance == Decimal("400.00")
