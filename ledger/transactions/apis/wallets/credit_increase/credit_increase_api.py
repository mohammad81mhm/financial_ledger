from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.serializers import SwaggerSerializer
from ledger.transactions.apis.wallets.credit_increase.credit_increase_serializers import (
    CreditIncreaseInputSerializer,
    CreditIncreaseOutputSerializer,
)
from ledger.transactions.constants import TRANSACTIONS_TAGS
from ledger.transactions.services import credit_increase


@extend_schema(tags=TRANSACTIONS_TAGS)
class WalletCreditIncreaseApi(AuthMixin, APIView):
    """Credit funds into a wallet owned by the authenticated user."""

    @extend_schema(
        summary="Credit Increase",
        description=(
            "Credits the specified wallet and records an immutable deposit transaction. "
            "Duplicate idempotency keys return the original transaction."
        ),
        request=CreditIncreaseInputSerializer,
        responses={
            201: SwaggerSerializer.wrap(CreditIncreaseOutputSerializer),
            200: SwaggerSerializer.wrap(CreditIncreaseOutputSerializer),
        },
    )
    def post(self, request, wallet_id: int) -> Response:
        """Credit a wallet for the authenticated user.

        Args:
            request: DRF request with credit increase payload.
            wallet_id (int): Target wallet primary key.

        Returns:
            Response: Created or existing transaction payload.
        """
        serializer = CreditIncreaseInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ledger_entry, is_duplicate = credit_increase(
            user=request.user,
            wallet_id=wallet_id,
            data=serializer.validated_data,
        )
        status_code = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED
        return Response(
            CreditIncreaseOutputSerializer(ledger_entry).data,
            status=status_code,
        )
