from rest_framework.exceptions import NotFound

from ledger.accounts.models import User
from ledger.wallets.selectors.wallet_selectors import get_wallet_for_user_by_id


def validate_wallet_filter(*, user: User, wallet_id: int | None) -> None:
    """Ensure an optional wallet filter targets a wallet owned by the user.

    Args:
        user (User): Authenticated user applying the filter.
        wallet_id (int | None): Optional wallet primary key from query params.

    Raises:
        NotFound: When wallet_id is provided but the wallet is missing or foreign.
    """
    if wallet_id is None:
        return

    if not get_wallet_for_user_by_id(user=user, wallet_id=wallet_id).exists():
        raise NotFound
