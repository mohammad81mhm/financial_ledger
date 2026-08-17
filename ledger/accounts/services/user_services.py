from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from ledger.accounts.models import User
from ledger.accounts.selectors.user_selectors import get_user_by_username, get_user_by_phone_number


@transaction.atomic
def create_user(*, data: dict) -> User:
    """Create a user from validated input data.

    Args:
        data (dict): Keys ``username``, ``password``, ``first_name``,
            ``last_name``, and ``phone_number``.

    Returns:
        User: The newly created user.

    Raises:
        ValidationError: When username or phone number is already taken, or a
            database constraint is violated.
    """
    if get_user_by_username(username=data["username"]).exists():
        raise ValidationError(_("A user with this username already exists."))
    if get_user_by_phone_number(phone_number=data["phone_number"]).exists():
        raise ValidationError(_("A user with this phone number already exists."))

    try:
        user = User(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone_number"],
        )
        user.set_password(data["password"])
        user.full_clean()
        user.save()
        return user
    except IntegrityError as exc:
        raise ValidationError(_("A database constraint was violated.")) from exc


@transaction.atomic
def create_superuser(*, data: dict) -> tuple[User, bool]:
    """Create a staff superuser from validated input data.

    Args:
        data (dict): Keys ``username``, ``password``, ``first_name``,
            ``last_name``, and ``phone_number``.

    Returns:
        tuple[User, bool]: The user and whether it was newly created.

    Raises:
        ValidationError: When the phone number is already taken, or a database
            constraint is violated.
    """
    existing = get_user_by_username(username=data["username"]).first()
    if existing is not None:
        return existing, False
    if get_user_by_phone_number(phone_number=data["phone_number"]).exists():
        raise ValidationError(_("A user with this phone number already exists."))

    try:
        user = User(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone_number"],
            is_staff=True,
            is_superuser=True,
        )
        user.set_password(data["password"])
        user.full_clean()
        user.save()
        return user, True
    except IntegrityError as exc:
        raise ValidationError(_("A database constraint was violated.")) from exc
