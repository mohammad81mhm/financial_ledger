from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.authentication.apis.register.register_serializers import RegisterInputSerializer
from ledger.authentication.apis.login.login_serializers import AuthOutputSerializer
from ledger.authentication.constants import AUTHENTICATION_TAGS
from ledger.authentication.services import register_user
from ledger.core.serializers import SwaggerSerializer


@extend_schema(tags=AUTHENTICATION_TAGS)
class RegisterApi(APIView):
    """Public registration that creates a user and returns JWT tokens."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        summary="Register New User",
        description="Creates a user and returns `access` and `refresh` tokens.",
        request=RegisterInputSerializer,
        responses={201: SwaggerSerializer.wrap(AuthOutputSerializer)},
    )
    def post(self, request) -> Response:
        """Register a new user.

        Args:
            request: DRF request with user create payload.

        Returns:
            Response: User and JWT tokens with HTTP 201.
        """
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, tokens = register_user(data=serializer.validated_data)
        return Response(
            AuthOutputSerializer({"user": user, "tokens": tokens}).data,
            status=status.HTTP_201_CREATED,
        )
