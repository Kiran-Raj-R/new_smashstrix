from django.urls import path
from . import views

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("add/", views.add_to_cart, name="add_to_cart"),
    path("item/<int:item_id>/increase/", views.increment_cart_item, name="increment_cart_item"),
    path("item/<int:item_id>/decrease/", views.decrement_cart_item, name="decrement_cart_item"),
    path("item/<int:item_id>/remove/", views.remove_from_cart, name="remove_from_cart"),
]
