import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordStrengthValidator:
    """Ensure passwords contain uppercase, lowercase, and special characters.

    This validator enforces that a password includes at least one lowercase
    letter, one uppercase letter, and one special (non-alphanumeric) character.
    """

    def validate(self, password: str, user=None) -> None:
        """Validate password strength requirements.

        Args:
            password (str): The password to validate.
            user: Optional user instance (unused, required by Django interface).

        Raises:
            ValidationError: When the password lacks required character types.
        """
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code="password_no_lowercase",
            )
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code="password_no_uppercase",
            )
        if not re.search(r"[^a-zA-Z0-9]", password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code="password_no_special",
            )

    def get_help_text(self) -> str:
        """Return a description of this validator's requirements.

        Returns:
            str: Human-readable help text.
        """
        return _(
            "Your password must contain at least one lowercase letter, one uppercase letter, and one special character."
        )
