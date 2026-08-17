from django.urls import include, path

urlpatterns = [
    path(
        "authentication/",
        include(("ledger.authentication.urls.authentication_urls", "authentication")),
    ),
    path(
        "wallets/",
        include(("ledger.wallets.urls.wallets_urls", "wallets")),
    ),
]
