from django.db.models import QuerySet

from ledger.accounts.models import User


def get_user_by_username(*, username: str) -> QuerySet[User]:
    """Return a queryset filtered to a single username.

    Args:
        username (str): Unique username.

    Returns:
        QuerySet[User]: Queryset with zero or one row.
    """
    return User.objects.filter(username=username)


def get_user_by_phone_number(*, phone_number: str) -> QuerySet[User]:
    """Return a queryset filtered to a single phone number.

    Args:
        phone_number (str): Unique phone number.

    Returns:
        QuerySet[User]: Queryset with zero or one row.
    """
    return User.objects.filter(phone_number=phone_number)
