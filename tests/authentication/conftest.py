import pytest
from django.urls import reverse


@pytest.fixture
def register_url() -> str:
    """Return the register API URL."""
    return reverse("api:authentication:register")


@pytest.fixture
def login_url() -> str:
    """Return the login API URL."""
    return reverse("api:authentication:login")


@pytest.fixture
def transaction_list_url() -> str:
    """Return the transaction list API URL used for JWT authorization checks."""
    return reverse("api:transactions:transaction-list")
