from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from ledger.accounts.validators import validate_iranian_phone_number
from ledger.core.models import BaseModel


class User(AbstractUser, BaseModel):
    """Application user with a phone number in addition to Django auth fields."""

    email = None  # unused; remove the inherited varchar(254) column

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Username"),
        help_text="Unique login name for this user.",
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name=_("First name"),
        help_text="Given name of the user.",
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_("Last name"),
        help_text="Family name of the user.",
    )
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[validate_iranian_phone_number],
        verbose_name=_("Phone number"),
        help_text="Iranian mobile phone number (11 digits starting with 09).",
    )

    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return self.username
