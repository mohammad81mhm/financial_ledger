from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.api.pagination import PageNumberPagination, get_paginated_response_context
from ledger.core.serializers import SwaggerSerializer
from ledger.transactions.apis.transactions.list.transaction_list_serializers import (
    TransactionListOutputSerializer,
)
from ledger.transactions.constants import TRANSACTIONS_TAGS
from ledger.transactions.filters.transaction_filters import TransactionFilter
from ledger.transactions.selectors import get_transactions_for_user


@extend_schema(tags=TRANSACTIONS_TAGS)
class TransactionListApi(AuthMixin, APIView):
    """List transactions for wallets owned by the authenticated user."""

    @extend_schema(
        summary="List Transactions",
        description=(
            "Returns paginated transaction history for wallets where the user is "
            "the sender or receiver."
        ),
        responses={200: SwaggerSerializer.wrap(TransactionListOutputSerializer, many=True)},
    )
    def get(self, request) -> Response:
        """Return paginated transactions for the authenticated user.

        Args:
            request: DRF request with optional filter query params.

        Returns:
            Response: Paginated transaction list.
        """
        transactions = get_transactions_for_user(user=request.user).order_by(
            "-created_at"
        )
        filterset = TransactionFilter(request.query_params, queryset=transactions)
        return get_paginated_response_context(
            pagination_class=PageNumberPagination,
            serializer_class=TransactionListOutputSerializer,
            queryset=filterset.qs,
            request=request,
            view=self,
        )
