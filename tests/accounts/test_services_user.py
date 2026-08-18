import pytest
from rest_framework.exceptions import ValidationError

from ledger.accounts.models import User
from ledger.accounts.services import create_superuser, create_user


@pytest.mark.django_db
def test_create_user_persists_hashed_password(user_data):
    """happy path: create_user stores all fields and hashes the password."""
    user = create_user(data=user_data)

    user.refresh_from_db()

    assert user.username == user_data["username"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert user.phone_number == user_data["phone_number"]
    assert user.check_password(user_data["password"])


@pytest.mark.django_db
def test_create_user_rejects_duplicate_username(user_data):
    """sad path: create_user rejects an already taken username."""
    create_user(data=user_data)

    with pytest.raises(ValidationError):
        create_user(data=user_data)


@pytest.mark.django_db
def test_create_user_rejects_duplicate_phone_number(user_data):
    """sad path: create_user rejects an already taken phone number."""
    create_user(data=user_data)
    duplicate_phone_data = {
        **user_data,
        "username": "another_username",
    }

    with pytest.raises(ValidationError):
        create_user(data=duplicate_phone_data)


@pytest.mark.django_db
def test_create_superuser_creates_staff_user(user_data):
    """happy path: create_superuser persists a staff superuser with a hashed password."""
    user, created = create_superuser(data=user_data)

    user.refresh_from_db()

    assert created is True
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password(user_data["password"])


@pytest.mark.django_db
def test_create_superuser_returns_existing_user(user_data):
    """happy path: create_superuser returns an existing user without creating a duplicate."""
    existing_user = create_user(data=user_data)

    user, created = create_superuser(data=user_data)

    assert created is False
    assert user.id == existing_user.id


@pytest.mark.django_db
def test_create_superuser_rejects_duplicate_phone_number(user_data):
    """sad path: create_superuser rejects an already taken phone number."""
    create_user(data=user_data)
    duplicate_phone_data = {
        **user_data,
        "username": "superuser_username",
    }

    with pytest.raises(ValidationError):
        create_superuser(data=duplicate_phone_data)
