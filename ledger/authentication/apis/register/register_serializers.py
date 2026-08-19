from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ledger.accounts.validators import validate_iranian_phone_number


class RegisterInputSerializer(serializers.Serializer):
    """Input payload for registering a user."""

    username = serializers.CharField(max_length=150, help_text="Unique login name for this user.")
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        help_text="Password for the user.",
    )
    first_name = serializers.CharField(max_length=150, help_text="Given name of the user.")
    last_name = serializers.CharField(max_length=150, help_text="Family name of the user.")
    phone_number = serializers.CharField(
        max_length=11,
        validators=[validate_iranian_phone_number],
        help_text="Iranian mobile phone number (11 digits starting with 09).",
    )
