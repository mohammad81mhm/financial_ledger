from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from ledger.accounts.models import User
from ledger.wallets.models import Wallet
from ledger.wallets.selectors.wallet_selectors import get_wallet_by_user_and_currency


@transaction.atomic
def create_wallet(*, user: User, data: dict) -> Wallet:
    """Create a wallet for a user in the requested currency.

    Args:
        user (User): Wallet owner.
        data (dict): Keys ``currency`` and optional ``initial_balance``.

    Returns:
        Wallet: The newly created wallet.

    Raises:
        ValidationError: When the user already has a wallet for that currency,
            the currency is invalid, or a database constraint is violated.
    """
    currency = data["currency"]
    initial_balance = data.get("initial_balance", 0)
    valid_currencies = {choice.value for choice in Wallet.Currency}
    if currency not in valid_currencies:
        raise ValidationError(_("Invalid currency."))

    if initial_balance < 0:
        raise ValidationError(_("Initial balance cannot be negative."))

    if get_wallet_by_user_and_currency(user=user, currency=currency).exists():
        raise ValidationError(_("You already have a wallet for this currency."))

    try:
        wallet = Wallet(
            user=user,
            currency=currency,
            balance=initial_balance,
        )
        wallet.full_clean()
        wallet.save()
        return wallet
    except IntegrityError as exc:
        raise ValidationError(_("A database constraint was violated.")) from exc
