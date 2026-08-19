import pytest
from django.urls import reverse
from model_bakery import baker

from ledger.wallets.models import Wallet


@pytest.fixture
def wallet_define_url() -> str:
    """Return the wallet define (create) API URL."""
    return reverse("api:wallets:wallet-define")


@pytest.fixture
def wallet_my_url() -> str:
    """Return the list-my-wallets API URL."""
    return reverse("api:wallets:wallet-my")


@pytest.fixture
def usd_wallet(user) -> Wallet:
    """Return a USD wallet owned by the default user."""
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.USD,
        balance=500,
    )


@pytest.fixture
def eur_wallet(user) -> Wallet:
    """Return a EUR wallet owned by the default user."""
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.EUR,
        balance=300,
    )
