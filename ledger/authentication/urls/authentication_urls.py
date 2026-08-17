from django.urls import path

from ledger.authentication.apis import LoginApi, RegisterApi

app_name = "authentication"

urlpatterns = [
    path("register/", RegisterApi.as_view(), name="register"),
    path("login/", LoginApi.as_view(), name="login"),
]
