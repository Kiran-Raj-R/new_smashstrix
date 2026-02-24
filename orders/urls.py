from django.urls import path
from . import views

urlpatterns = [
    path("",views.order_list, name="order_list"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("place-order/",views.place_order, name="place_order"),
    path("success/<str:order_id>/",views.order_success, name="order_success"),
    path("<str:order_id>/", views.order_detail,name="order_detail"),
    path("cancel/<str:order_id>/",views.cancel_order,name="cancel_order"),

]