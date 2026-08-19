import pytest
from django.urls import reverse
from model_bakery import baker

from ledger.wallets.models import Wallet


@pytest.fixture
def credit_increase_url(wallet) -> str:
    """Return the credit-increase API URL for the default wallet."""
    return reverse(
        "api:transactions:wallet-credit-increase",
        kwargs={"wallet_id": wallet.id},
    )


@pytest.fixture
def transaction_list_url() -> str:
    """Return the transaction list API URL."""
    return reverse("api:transactions:transaction-list")


@pytest.fixture
def transaction_detail_url():
    """Return a callable that builds the transaction detail API URL."""

    def _build(*, transaction_id) -> str:
        return reverse(
            "api:transactions:transaction-detail",
            kwargs={"transaction_id": transaction_id},
        )

    return _build


@pytest.fixture
def wallet(user) -> Wallet:
    """Return a USD wallet owned by the default user."""
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.USD,
        balance=1000,
    )


@pytest.fixture
def wallet_eur(user) -> Wallet:
    """Return a EUR wallet owned by the default user."""
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.EUR,
        balance=500,
    )


@pytest.fixture
def receiver_wallet(other_user) -> Wallet:
    """Return a USD wallet owned by the secondary user."""
    return baker.make(
        Wallet,
        user=other_user,
        currency=Wallet.Currency.USD,
        balance=200,
    )
