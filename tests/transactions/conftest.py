import pytest
from model_bakery import baker

from ledger.wallets.models import Wallet


@pytest.fixture
def wallet(user) -> Wallet:
    """Return a USD wallet owned by the default user."""
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.USD,
        balance="1000.00",
    )


@pytest.fixture
def wallet_eur(user) -> Wallet:
    """Return a EUR wallet owned by the default user."""
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.EUR,
        balance="500.00",
    )


@pytest.fixture
def receiver_wallet(other_user) -> Wallet:
    """Return a USD wallet owned by the secondary user."""
    return baker.make(
        Wallet,
        user=other_user,
        currency=Wallet.Currency.USD,
        balance="200.00",
    )
