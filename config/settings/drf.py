from config.env import env

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "PAGE_SIZE": env.int("PAGE_SIZE", default=10),
    "MAX_PAGE_SIZE": env.int("MAX_PAGE_SIZE", default=10000),
    "DEFAULT_PAGINATION_CLASS": "ledger.core.api.pagination.PageNumberPagination",
    "DEFAULT_RENDERER_CLASSES": ["ledger.core.api.renderers.CustomJSONRenderer"],
}
