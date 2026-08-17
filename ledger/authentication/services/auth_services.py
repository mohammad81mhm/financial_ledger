from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from ledger.accounts.models import User
from ledger.accounts.services import create_user


def create_token_pair(*, user: User) -> dict[str, str]:
    """Issue JWT access and refresh tokens for a user.

    Args:
        user (User): Authenticated user.

    Returns:
        dict[str, str]: Mapping with ``access`` and ``refresh`` token strings.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def register_user(*, data: dict) -> tuple[User, dict[str, str]]:
    """Register a new user and return JWT tokens.

    Args:
        data (dict): Validated create-user payload.

    Returns:
        tuple[User, dict[str, str]]: Created user and token pair.
    """
    user = create_user(data=data)
    tokens = create_token_pair(user=user)
    return user, tokens


def login_user(*, username: str, password: str) -> tuple[User, dict[str, str]]:
    """Authenticate a user and return JWT tokens.

    Args:
        username (str): Login username.
        password (str): Plain-text password.

    Returns:
        tuple[User, dict[str, str]]: Authenticated user and token pair.

    Raises:
        ValidationError: When credentials are invalid or the user is inactive.
    """
    user = authenticate(username=username, password=password)
    if user is None or not user.is_active:
        raise ValidationError(_("Invalid username or password."))
    tokens = create_token_pair(user=user)
    return user, tokens
