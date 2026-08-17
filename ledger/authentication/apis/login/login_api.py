from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.authentication.apis.login.login_serializers import (
    AuthOutputSerializer,
    LoginInputSerializer,
)
from ledger.authentication.constants import AUTHENTICATION_TAGS
from ledger.authentication.services import login_user
from ledger.core.serializers import SwaggerSerializer


@extend_schema(tags=AUTHENTICATION_TAGS)
class LoginApi(APIView):
    """Authenticate with username and password and return JWT tokens."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    @extend_schema(
        summary="Login New User",
        description="Validates credentials and returns `access` and `refresh` tokens.",
        request=LoginInputSerializer,
        responses=SwaggerSerializer.wrap(AuthOutputSerializer),
    )
    def post(self, request) -> Response:
        """Log in a user.

        Args:
            request: DRF request with username and password.

        Returns:
            Response: User and JWT tokens.
        """
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, tokens = login_user(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        return Response(AuthOutputSerializer({"user": user, "tokens": tokens}).data)
