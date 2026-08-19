"""Tests for Iranian phone number validator."""

import pytest
from django.core.exceptions import ValidationError

from ledger.accounts.validators import validate_iranian_phone_number


class TestValidateIranianPhoneNumber:
    """Tests for validate_iranian_phone_number."""

    @pytest.mark.parametrize(
        "phone",
        [
            "09121234567",
            "09351234567",
            "09901234567",
            "09010000000",
        ],
    )
    def test_accepts_valid_iranian_numbers(self, phone):
        """happy path: valid 11-digit Iranian numbers starting with 09 pass."""
        validate_iranian_phone_number(phone)

    @pytest.mark.parametrize(
        "phone,reason",
        [
            ("0912123456", "too short (10 digits)"),
            ("091212345678", "too long (12 digits)"),
            ("19121234567", "does not start with 0"),
            ("08121234567", "starts with 08 instead of 09"),
            ("0912abc4567", "contains letters"),
            ("", "empty string"),
            ("09 12 123 4567", "contains spaces"),
            ("+989121234567", "international format not allowed"),
        ],
    )
    def test_rejects_invalid_numbers(self, phone, reason):
        """sad path: invalid phone numbers raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_iranian_phone_number(phone)

        assert exc_info.value.code == "invalid_phone_number"


@pytest.mark.django_db
class TestPhoneValidatorIntegration:
    """Integration tests ensuring phone validation works through create_user."""

    def test_create_user_rejects_invalid_phone(self):
        """sad path: create_user rejects a non-Iranian phone number."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        from ledger.accounts.services import create_user

        data = {
            "username": "badphone_user",
            "password": "SecurePass1",
            "first_name": "Bad",
            "last_name": "Phone",
            "phone_number": "1234567890",
        }

        with pytest.raises(DjangoValidationError):
            create_user(data=data)

    def test_register_api_rejects_invalid_phone(self, api_client):
        """sad path: register API rejects a non-Iranian phone number."""
        from django.urls import reverse
        from rest_framework import status

        url = reverse("api:authentication:register")
        payload = {
            "username": "badphone_api",
            "password": "SecurePass1",
            "first_name": "Bad",
            "last_name": "Phone",
            "phone_number": "1234567890",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
