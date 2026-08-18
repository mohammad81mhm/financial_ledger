from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.serializers import SwaggerSerializer
from ledger.transactions.apis.wallets.credit_decrease.credit_decrease_serializers import (
    CreditDecreaseInputSerializer,
    CreditDecreaseOutputSerializer,
)
from ledger.transactions.constants import TRANSACTIONS_TAGS
from ledger.transactions.services import credit_decrease


@extend_schema(tags=TRANSACTIONS_TAGS)
class WalletCreditDecreaseApi(AuthMixin, APIView):
    """Debit funds from a wallet owned by the authenticated user."""

    @extend_schema(
        summary="Credit Decrease",
        description=(
            "Debits the specified wallet and records an immutable withdrawal transaction. "
            "Duplicate idempotency keys return the original transaction."
        ),
        request=CreditDecreaseInputSerializer,
        responses={
            201: SwaggerSerializer.wrap(CreditDecreaseOutputSerializer),
            200: SwaggerSerializer.wrap(CreditDecreaseOutputSerializer),
        },
    )
    def post(self, request, wallet_id: int) -> Response:
        """Debit a wallet for the authenticated user.

        Args:
            request: DRF request with credit decrease payload.
            wallet_id (int): Target wallet primary key.

        Returns:
            Response: Created or existing transaction payload.
        """
        serializer = CreditDecreaseInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ledger_entry, is_duplicate = credit_decrease(
            user=request.user,
            wallet_id=wallet_id,
            data=serializer.validated_data,
        )
        status_code = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED
        return Response(
            CreditDecreaseOutputSerializer(ledger_entry).data,
            status=status_code,
        )
