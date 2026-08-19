from django.urls import path

from ledger.transactions.apis.transfers.transfer_api import TransferApi

app_name = "transfers"

urlpatterns = [
    path("", TransferApi.as_view(), name="transfer"),
]
