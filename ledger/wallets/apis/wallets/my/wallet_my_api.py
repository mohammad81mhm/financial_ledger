from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.api.pagination import PageNumberPagination, get_paginated_response_context
from ledger.core.serializers import SwaggerSerializer
from ledger.wallets.apis.wallets.my.wallet_my_serializers import WalletMyOutputSerializer
from ledger.wallets.constants import WALLETS_TAGS
from ledger.wallets.selectors import get_wallets_for_user


@extend_schema(tags=WALLETS_TAGS)
class WalletMyApi(AuthMixin, APIView):
    """List wallets owned by the authenticated user."""

    @extend_schema(
        summary="List My Wallets",
        description="Returns wallets owned by the authenticated user.",
        responses={200: SwaggerSerializer.wrap(WalletMyOutputSerializer, many=True)},
    )
    def get(self, request) -> Response:
        """List wallets for the current user.

        Args:
            request: DRF request.

        Returns:
            Response: Paginated list of wallets.
        """
        wallets = get_wallets_for_user(user=request.user).order_by("-created_at")
        return get_paginated_response_context(
            pagination_class=PageNumberPagination,
            serializer_class=WalletMyOutputSerializer,
            queryset=wallets,
            request=request,
            view=self,
        )
