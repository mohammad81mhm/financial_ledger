from django.conf import settings
from django.db.models import QuerySet
from rest_framework.pagination import PageNumberPagination as _PageNumberPagination
from rest_framework.settings import api_settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView


class PageNumberPagination(_PageNumberPagination):
    """Page-number pagination using ``p`` and ``page_size`` query params."""

    page_query_param = "p"
    page_size_query_param = "page_size"
    page_size = api_settings.PAGE_SIZE
    max_page_size = settings.REST_FRAMEWORK["MAX_PAGE_SIZE"]


def get_paginated_response_context(
    *,
    pagination_class: type[PageNumberPagination],
    serializer_class: type[BaseSerializer],
    queryset: QuerySet,
    request: Request,
    view: APIView,
) -> Response:
    """Serialize a queryset with request context and return a paginated response.

    Args:
        pagination_class (type[PageNumberPagination]): Pagination class to use.
        serializer_class (type[BaseSerializer]): Serializer for each row.
        queryset (QuerySet): Queryset to paginate.
        request (Request): Current DRF request.
        view (APIView): View that owns the queryset.

    Returns:
        Response: Paginated payload, or the full serialized list when pagination
            is skipped.
    """
    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True, context={"request": request})
    return Response(data=serializer.data)
