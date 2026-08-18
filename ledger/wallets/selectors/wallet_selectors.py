from django.db.models import QuerySet

from ledger.accounts.models import User
from ledger.wallets.models import Wallet


def get_wallets_for_user(*, user: User) -> QuerySet[Wallet]:
    """Return all wallets owned by a user.

    Args:
        user (User): Wallet owner.

    Returns:
        QuerySet[Wallet]: Wallets for the given user.
    """
    return Wallet.objects.filter(user=user)


def get_wallet_by_user_and_currency(*, user: User, currency: str) -> QuerySet[Wallet]:
    """Return wallets filtered by owner and currency.

    Args:
        user (User): Wallet owner.
        currency (str): Currency code such as USD, EUR, or IRR.

    Returns:
        QuerySet[Wallet]: Queryset with zero or one row.
    """
    return Wallet.objects.filter(user=user, currency=currency)
