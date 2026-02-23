from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("place-order/",views.place_order, name="place_order"),
    path("success/<str:order_id>/",views.order_success, name="order_success"),
    
]