from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ledger.core.api.mixins import AuthMixin
from ledger.core.api.pagination import PageNumberPagination, get_paginated_response_context
from ledger.core.serializers import SwaggerSerializer
from ledger.transactions.apis.transactions.list.transaction_list_serializers import (
    TransactionListInputSerializer,
    TransactionListOutputSerializer,
)
from ledger.transactions.constants import TRANSACTIONS_TAGS
from ledger.transactions.filters.transaction_filters import TransactionFilter
from ledger.transactions.selectors import get_transactions_for_user
from ledger.transactions.services import validate_wallet_filter

_PAGINATION_PARAMS = {"p", "page_size"}


@extend_schema(tags=TRANSACTIONS_TAGS)
class TransactionListApi(AuthMixin, APIView):
    """List transactions for wallets owned by the authenticated user."""

    @extend_schema(
        summary="List my transactions",
        description=(
            "Returns a paginated list of transactions where the authenticated user "
            "owns the sender or receiver wallet.\n\n"
            "Pagination: use p (page number) and page_size (items per page). "
            "Default page size comes from settings.\n\n"
            "Date filters: from_date and to_date filter by created_at "
            "(inclusive, date-only).\n\n"
            "Advanced filters:\n"
            "- transaction_type — DEPOSIT, WITHDRAWAL, or TRANSFER\n"
            "- status — PENDING, COMPLETED, or FAILED\n"
            "- wallet_id — scope to one owned wallet (404 if not yours)\n"
            "- currency — USD, EUR, or IRR\n"
            "- min_amount / max_amount — filter by transaction amount (whole units)\n\n"
            "Results are always sorted by created_at descending (newest first)."
        ),
        parameters=[TransactionListInputSerializer],
        responses={200: SwaggerSerializer.wrap(TransactionListOutputSerializer, many=True)},
    )
    def get(self, request) -> Response:
        """Return paginated transactions for the authenticated user.

        Args:
            request: DRF request with optional filter query params.

        Returns:
            Response: Paginated transaction list.
        """
        input_serializer = TransactionListInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        validate_wallet_filter(
            user=request.user,
            wallet_id=validated.get("wallet_id"),
        )

        filter_data = {
            key: value
            for key, value in validated.items()
            if key not in _PAGINATION_PARAMS and value is not None
        }

        transactions = get_transactions_for_user(user=request.user).order_by(
            "-created_at"
        )
        filterset = TransactionFilter(filter_data, queryset=transactions)
        return get_paginated_response_context(
            pagination_class=PageNumberPagination,
            serializer_class=TransactionListOutputSerializer,
            queryset=filterset.qs,
            request=request,
            view=self,
        )
