from django.urls import path

from ledger.wallets.apis import WalletDefineApi, WalletMyApi

app_name = "wallets"

urlpatterns = [
    path("define/", WalletDefineApi.as_view(), name="wallet-define"),
    path("my/", WalletMyApi.as_view(), name="wallet-my"),
]
