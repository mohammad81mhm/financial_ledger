import pytest
from rest_framework.exceptions import ValidationError

from ledger.wallets.models import Wallet
from ledger.wallets.services import create_wallet


@pytest.mark.django_db
def test_create_wallet_success(user):
    """happy path: create_wallet persists a wallet with the requested currency and balance."""
    data = {"currency": "USD", "initial_balance": 100}

    wallet = create_wallet(user=user, data=data)

    assert wallet.pk is not None
    assert wallet.user_id == user.id
    assert wallet.currency == Wallet.Currency.USD
    assert wallet.balance == 100


@pytest.mark.django_db
def test_create_wallet_defaults_balance_to_zero(user):
    """happy path: create_wallet defaults initial_balance to zero when omitted."""
    data = {"currency": "EUR"}

    wallet = create_wallet(user=user, data=data)

    assert wallet.balance == 0


@pytest.mark.django_db
def test_create_wallet_rejects_duplicate_currency(user, usd_wallet):
    """sad path: create_wallet rejects a second wallet for the same currency."""
    data = {"currency": "USD"}

    with pytest.raises(ValidationError, match="already have a wallet"):
        create_wallet(user=user, data=data)


@pytest.mark.django_db
def test_create_wallet_rejects_invalid_currency(user):
    """sad path: create_wallet rejects an unsupported currency code."""
    data = {"currency": "GBP"}

    with pytest.raises(ValidationError, match="Invalid currency"):
        create_wallet(user=user, data=data)


@pytest.mark.django_db
def test_create_wallet_rejects_negative_balance(user):
    """sad path: create_wallet rejects a negative initial balance."""
    data = {"currency": "USD", "initial_balance": -10}

    with pytest.raises(ValidationError, match="negative"):
        create_wallet(user=user, data=data)
