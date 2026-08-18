from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.serializers import SwaggerSerializer
from ledger.transactions.apis.transfers.transfer_serializers import (
    TransferInputSerializer,
    TransferOutputSerializer,
)
from ledger.transactions.constants import TRANSACTIONS_TAGS
from ledger.transactions.services import transfer_between_wallets


@extend_schema(tags=TRANSACTIONS_TAGS)
class TransferApi(AuthMixin, APIView):
    """Transfer funds between two wallets."""

    @extend_schema(
        summary="Transfer Between Wallets",
        description=(
            "Moves funds from the sender wallet to the receiver wallet atomically. "
            "The sender wallet must belong to the authenticated user."
        ),
        request=TransferInputSerializer,
        responses={
            201: SwaggerSerializer.wrap(TransferOutputSerializer),
            200: SwaggerSerializer.wrap(TransferOutputSerializer),
        },
    )
    def post(self, request) -> Response:
        """Transfer funds between two wallets.

        Args:
            request: DRF request with transfer payload.

        Returns:
            Response: Created or existing transaction payload.
        """
        serializer = TransferInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ledger_entry, is_duplicate = transfer_between_wallets(
            user=request.user,
            data=serializer.validated_data,
        )
        status_code = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED
        return Response(
            TransferOutputSerializer(ledger_entry).data,
            status=status_code,
        )
