from rest_framework import serializers

from ledger.accounts.models import User


class UserOutputSerializer(serializers.ModelSerializer):
    """Public user fields returned by APIs."""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "phone_number"]
        extra_kwargs = {
            "id": {"help_text": "Primary key of the user."},
            "username": {"help_text": "Unique login name for this user."},
            "first_name": {"help_text": "Given name of the user."},
            "last_name": {"help_text": "Family name of the user."},
            "phone_number": {"help_text": "Mobile phone number used to identify the user."},
        }
