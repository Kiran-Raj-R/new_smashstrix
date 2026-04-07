from django.urls import path
from . import views

urlpatterns = [
    path("",views.order_list, name="order_list"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("place-order/",views.place_order, name="place_order"),
    path("create-razorpay-order/", views.create_razorpay_order, name="create_razorpay_order"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path("success/<str:order_id>/",views.order_success, name="order_success"),
    path("cancel/<str:order_id>/",views.cancel_order,name="cancel_order"),
    path("cancel-item/<int:item_id>/",views.cancel_order_item, name="cancel_order_item"),
    path("item-return/<int:item_id>/",views.request_item_return, name="request_item_return"),
    path("invoice/<str:order_id>/",views.download_invoice, name="download_invoice"),
    path("<str:order_id>/", views.order_detail,name="order_detail"),

]