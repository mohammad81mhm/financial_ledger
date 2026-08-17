from rest_framework import serializers

from ledger.accounts.apis.users.user_serializers import UserOutputSerializer


class TokenOutputSerializer(serializers.Serializer):
    """JWT access and refresh tokens."""

    access = serializers.CharField(help_text="JWT access token.")
    refresh = serializers.CharField(help_text="JWT refresh token.")


class AuthOutputSerializer(serializers.Serializer):
    """User plus JWT tokens returned after register or login."""

    user = UserOutputSerializer(help_text="Authenticated user profile.")
    tokens = TokenOutputSerializer(help_text="JWT access and refresh tokens.")


class LoginInputSerializer(serializers.Serializer):
    """Input payload for login."""

    username = serializers.CharField(max_length=150, help_text="Unique login name for this user.")
    password = serializers.CharField(write_only=True, help_text="Password for the user.")
