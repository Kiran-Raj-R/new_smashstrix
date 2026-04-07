from django.urls import path
from . import views

urlpatterns = [
    path("", views.wallet_detail, name="wallet_detail"),
    path("create-order/", views.create_wallet_order, name="create_wallet_order"),
    path("verify/", views.verify_wallet_payment, name="verify_wallet_payment"),

]