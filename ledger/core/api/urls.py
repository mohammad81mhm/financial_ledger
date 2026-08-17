from django.urls import include, path

urlpatterns = [
    path(
        "authentication/",
        include(("ledger.authentication.urls.authentication_urls", "authentication")),
    ),
]
