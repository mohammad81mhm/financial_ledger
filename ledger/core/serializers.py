from rest_framework import serializers


class SwaggerSerializer(serializers.Serializer):
    """OpenAPI wrapper matching the custom JSON response envelope."""

    result = serializers.JSONField(help_text="Endpoint payload.")
    status = serializers.IntegerField(help_text="HTTP status code.")
    success = serializers.BooleanField(help_text="Whether the request succeeded.")
    messages = serializers.ListField(help_text="Success or error messages.")

    @classmethod
    def wrap(
        cls,
        result_serializer: type[serializers.BaseSerializer],
        *,
        many: bool = False,
    ) -> type[serializers.Serializer]:
        """Return an envelope serializer whose ``result`` uses ``result_serializer``.

        Args:
            result_serializer (type[serializers.BaseSerializer]): Output serializer
                for the ``result`` field.
            many (bool): Whether ``result`` is a list of that serializer.

        Returns:
            type[serializers.Serializer]: Envelope class for ``extend_schema``.
        """
        suffix = "ListEnvelope" if many else "Envelope"
        envelope_ref_name = f"{result_serializer.__name__}{suffix}"

        class WrappedSwaggerSerializer(cls):
            result = result_serializer(many=many, help_text="Endpoint payload.")

            class Meta:
                pass

        WrappedSwaggerSerializer.Meta.ref_name = envelope_ref_name
        WrappedSwaggerSerializer.__name__ = envelope_ref_name
        WrappedSwaggerSerializer.__qualname__ = envelope_ref_name
        return WrappedSwaggerSerializer
