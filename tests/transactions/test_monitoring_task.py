from unittest.mock import patch
from uuid import uuid4

import pytest

from ledger.transactions.services import transfer_between_wallets


@pytest.mark.django_db
def test_high_value_transfer_triggers_monitoring_task(user, wallet, receiver_wallet):
    """happy path: high-value transfers schedule a monitoring task after commit."""
    wallet.balance = 20000
    wallet.save(update_fields=["balance"])

    with patch(
        "ledger.transactions.services.transaction_services.notify_monitoring_team.delay"
    ) as mock_delay, patch(
        "ledger.transactions.services.transaction_services.transaction.on_commit",
        side_effect=lambda callback: callback(),
    ):
        transfer_between_wallets(
            user=user,
            data={
                "sender_wallet_id": wallet.id,
                "receiver_wallet_id": receiver_wallet.id,
                "amount": 15000,
                "idempotency_key": uuid4(),
            },
        )

    mock_delay.assert_called_once()
