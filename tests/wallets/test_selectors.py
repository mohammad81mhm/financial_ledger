"""Tests for ledger.wallets.selectors."""

import pytest
from model_bakery import baker

from ledger.wallets.models import Wallet
from ledger.wallets.selectors import (
    get_wallet_by_id,
    get_wallet_by_user_and_currency,
    get_wallet_for_user_by_id,
    get_wallets_for_user,
)


@pytest.mark.django_db
def test_get_wallets_for_user_returns_owned_wallets(user, usd_wallet, eur_wallet):
    """happy path: returns all wallets belonging to the user."""
    qs = get_wallets_for_user(user=user)

    assert qs.count() == 2
    assert set(qs.values_list("id", flat=True)) == {usd_wallet.id, eur_wallet.id}


@pytest.mark.django_db
def test_get_wallets_for_user_excludes_other_users(user, other_user, usd_wallet):
    """happy path: does not return wallets owned by another user."""
    baker.make(Wallet, user=other_user, currency=Wallet.Currency.IRR)

    qs = get_wallets_for_user(user=user)

    assert qs.count() == 1


@pytest.mark.django_db
def test_get_wallet_by_user_and_currency(user, usd_wallet):
    """happy path: filters by user and currency."""
    qs = get_wallet_by_user_and_currency(user=user, currency="USD")

    assert qs.get() == usd_wallet


@pytest.mark.django_db
def test_get_wallet_by_id(usd_wallet):
    """happy path: returns wallet by primary key."""
    qs = get_wallet_by_id(wallet_id=usd_wallet.id)

    assert qs.get() == usd_wallet


@pytest.mark.django_db
def test_get_wallet_for_user_by_id(user, usd_wallet):
    """happy path: returns wallet matching both user and id."""
    qs = get_wallet_for_user_by_id(user=user, wallet_id=usd_wallet.id)

    assert qs.get() == usd_wallet


@pytest.mark.django_db
def test_get_wallet_for_user_by_id_excludes_foreign(other_user, usd_wallet):
    """sad path: does not return a wallet belonging to another user."""
    qs = get_wallet_for_user_by_id(user=other_user, wallet_id=usd_wallet.id)

    assert qs.exists() is False
