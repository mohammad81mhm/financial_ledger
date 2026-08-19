from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.serializers import SwaggerSerializer
from ledger.wallets.apis.wallets.define.wallet_define_serializers import (
    WalletDefineInputSerializer,
    WalletOutputSerializer,
)
from ledger.wallets.constants import WALLETS_TAGS
from ledger.wallets.services import create_wallet


@extend_schema(tags=WALLETS_TAGS)
class WalletDefineApi(AuthMixin, APIView):
    """Create a wallet for the authenticated user."""

    @extend_schema(
        summary="Create Wallet",
        description=(
            "Creates a wallet in the requested currency. Each user may have only one wallet per currency. "
            "Initial balance is optional and defaults to zero."
        ),
        request=WalletDefineInputSerializer,
        responses={201: SwaggerSerializer.wrap(WalletOutputSerializer)},
    )
    def post(self, request) -> Response:
        """Create a wallet for the current user.

        Args:
            request: DRF request with wallet create payload.

        Returns:
            Response: Created wallet with HTTP 201.
        """
        serializer = WalletDefineInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet = create_wallet(user=request.user, data=serializer.validated_data)
        return Response(
            WalletOutputSerializer(wallet).data,
            status=status.HTTP_201_CREATED,
        )
