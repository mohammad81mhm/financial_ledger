import pytest
from django.core.management import call_command
from model_bakery import baker

from ledger.transactions.constants import DEFAULT_WALLET_TRANSFER_LIMIT
from ledger.wallets.models import Wallet


@pytest.mark.django_db
def test_reset_wallet_limitations_restores_default_limit(user, other_user):
    """happy path: command sets every wallet remaining_limit to the default."""
    first = baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.USD,
        remaining_limit=0,
    )
    second = baker.make(
        Wallet,
        user=other_user,
        currency=Wallet.Currency.USD,
        remaining_limit=7,
    )

    call_command("reset_wallet_limitations")

    first.refresh_from_db()
    second.refresh_from_db()
    assert first.remaining_limit == DEFAULT_WALLET_TRANSFER_LIMIT
    assert second.remaining_limit == DEFAULT_WALLET_TRANSFER_LIMIT
