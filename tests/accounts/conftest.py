import pytest
from django.urls import reverse


@pytest.fixture
def register_url() -> str:
    """Return the register API URL."""
    return reverse("api:authentication:register")
