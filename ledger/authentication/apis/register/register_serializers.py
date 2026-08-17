from rest_framework import serializers


class RegisterInputSerializer(serializers.Serializer):
    """Input payload for registering a user."""
    username = serializers.CharField(max_length=150, help_text="Unique login name for this user.")
    password = serializers.CharField(write_only=True, min_length=8, help_text="Password for the user.")
    first_name = serializers.CharField(max_length=150, help_text="Given name of the user.")
    last_name = serializers.CharField(max_length=150, help_text="Family name of the user.")
    phone_number = serializers.CharField(max_length=20, help_text="Mobile phone number used to identify the user.")
