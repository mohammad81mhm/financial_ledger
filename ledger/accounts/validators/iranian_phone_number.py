import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_iranian_phone_number(value: str) -> None:
    """Validate that the value is an Iranian mobile number with exactly 11 digits.

    The number must start with '09' followed by 9 digits.

    Args:
        value (str): Phone number string to validate.

    Raises:
        ValidationError: When the value does not match the Iranian phone format.
    """
    pattern = r"^09\d{9}$"
    if not re.match(pattern, value):
        raise ValidationError(
            _("Enter a valid Iranian phone number (11 digits starting with 09)."),
            code="invalid_phone_number",
        )
