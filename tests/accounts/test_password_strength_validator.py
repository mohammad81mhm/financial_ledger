"""Tests for the password strength validator."""

import pytest
from django.core.exceptions import ValidationError

from ledger.accounts.validators.password_strength import PasswordStrengthValidator


class TestPasswordStrengthValidator:
    """Unit tests for PasswordStrengthValidator."""

    def setup_method(self):
        """Instantiate the validator for each test."""
        self.validator = PasswordStrengthValidator()

    @pytest.mark.parametrize(
        "password",
        [
            "Secure@1",
            "Hello!World9",
            "myP@ssw0rd",
            "Abc#1234",
        ],
    )
    def test_accepts_strong_passwords(self, password):
        """happy path: passwords with lower, upper, and special chars pass."""
        self.validator.validate(password)

    def test_rejects_missing_lowercase(self):
        """sad path: password without lowercase letter raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate("ALLUPPERCASE@1")

        assert exc_info.value.code == "password_no_lowercase"

    def test_rejects_missing_uppercase(self):
        """sad path: password without uppercase letter raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate("alllowercase@1")

        assert exc_info.value.code == "password_no_uppercase"

    def test_rejects_missing_special_char(self):
        """sad path: password without special character raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate("NoSpecial123")

        assert exc_info.value.code == "password_no_special"

    def test_get_help_text_returns_string(self):
        """happy path: get_help_text returns a non-empty description."""
        help_text = self.validator.get_help_text()

        assert "lowercase" in help_text
        assert "uppercase" in help_text
        assert "special" in help_text


@pytest.mark.django_db
class TestPasswordValidatorIntegration:
    """Integration tests ensuring password validator works with register API."""

    def test_register_rejects_no_uppercase(self, api_client, register_url):
        """sad path: register API rejects password without uppercase."""
        from rest_framework import status

        payload = {
            "username": "weakpass_user",
            "password": "alllower@1",
            "first_name": "Weak",
            "last_name": "Pass",
            "phone_number": "09121111111",
        }

        response = api_client.post(register_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_rejects_no_special_char(self, api_client, register_url):
        """sad path: register API rejects password without special character."""
        from rest_framework import status

        payload = {
            "username": "weakpass_user2",
            "password": "NoSpecial123",
            "first_name": "Weak",
            "last_name": "Pass",
            "phone_number": "09122222222",
        }

        response = api_client.post(register_url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_accepts_strong_password(self, api_client, register_url):
        """happy path: register API accepts a password meeting all requirements."""
        from rest_framework import status

        payload = {
            "username": "strongpass_user",
            "password": "Strong@Pass1",
            "first_name": "Strong",
            "last_name": "Pass",
            "phone_number": "09123333333",
        }

        response = api_client.post(register_url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
