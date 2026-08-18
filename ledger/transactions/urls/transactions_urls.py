from django.urls import path

from ledger.transactions.apis import WalletCreditDecreaseApi, WalletCreditIncreaseApi

app_name = "transactions"

urlpatterns = [
    path(
        "wallets/<int:wallet_id>/credit-increase/",
        WalletCreditIncreaseApi.as_view(),
        name="wallet-credit-increase",
    ),
    path(
        "wallets/<int:wallet_id>/credit-decrease/",
        WalletCreditDecreaseApi.as_view(),
        name="wallet-credit-decrease",
    ),
]
