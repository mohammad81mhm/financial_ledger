import pytest
from model_bakery import baker

from ledger.accounts.models import User
from ledger.wallets.models import Wallet


@pytest.fixture
def user(db) -> User:
    """ 
    User factory.
    """
    return baker.make(
        User,
        username="wallet_user",
        phone_number="10000000001",
    )


@pytest.fixture
def other_user(db) -> User:
    """
    Other user factory.
    """
    return baker.make(
        User,
        username="other_user",
        phone_number="10000000002",
    )


@pytest.fixture
def wallet(user) -> Wallet:
    """
    Wallet factory.
    """
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.USD,
        balance="1000.00",
    )


@pytest.fixture
def wallet_eur(user) -> Wallet:
    """
    Wallet factory for EUR.
    """
    return baker.make(
        Wallet,
        user=user,
        currency=Wallet.Currency.EUR,
        balance="500.00",
    )


@pytest.fixture
def receiver_wallet(other_user) -> Wallet:
    """
    Receiver wallet factory.
    """
    return baker.make(
        Wallet,
        user=other_user,
        currency=Wallet.Currency.USD,
        balance="200.00",
    )
