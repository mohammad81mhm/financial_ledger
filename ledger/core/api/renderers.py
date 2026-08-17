from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_success


class CustomJSONRenderer(JSONRenderer):
    """Wrap every API payload in a ``result`` / ``status`` / ``success`` / ``messages`` envelope."""

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict[str, Any] | None = None,
    ) -> bytes:
        """Render the response body inside the standard envelope.

        Args:
            data (Any): View payload or error body.
            accepted_media_type (str | None): Negotiated media type.
            renderer_context (dict[str, Any] | None): DRF renderer context.

        Returns:
            bytes: Encoded JSON envelope.
        """
        renderer_context = renderer_context or {}
        response = renderer_context["response"]
        success = is_success(response.status_code)
        envelope = {
            "result": data if success else [],
            "status": response.status_code,
            "success": success,
            "messages": {"success": [_("The operation was successful")]} if success else data,
        }
        return super().render(envelope, accepted_media_type, renderer_context)
