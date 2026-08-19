from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.serializers import SwaggerSerializer
from ledger.transactions.apis.transactions.detail.transaction_detail_serializers import (
    TransactionDetailOutputSerializer,
)
from ledger.transactions.constants import TRANSACTIONS_TAGS
from ledger.transactions.selectors import get_transactions_for_user


@extend_schema(tags=TRANSACTIONS_TAGS)
class TransactionDetailApi(AuthMixin, APIView):
    """Retrieve a single transaction for the authenticated user."""

    @extend_schema(
        summary="Retrieve Transaction",
        description=("Returns one transaction when the authenticated user owns the sender or receiver wallet."),
        responses={200: SwaggerSerializer.wrap(TransactionDetailOutputSerializer)},
    )
    def get(self, request, transaction_id: UUID) -> Response:
        """Return one transaction owned by the authenticated user.

        Args:
            request: DRF request.
            transaction_id (UUID): Transaction primary key.

        Returns:
            Response: Transaction payload.
        """
        transactions = get_transactions_for_user(user=request.user)
        ledger_entry = get_object_or_404(transactions, id=transaction_id)
        return Response(TransactionDetailOutputSerializer(ledger_entry).data)
