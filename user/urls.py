from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('shop/',views.shop,name='shop'),
    path('profile/',views.user_profile,name='profile'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/email/verify/", views.verify_email_change_otp, name="verify_email_change"),
    path("profile/email/resend/", views.resend_email_change_otp, name="resend_email_change"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path('product/<int:product_id>/', views.product_detail, name="product_detail"),
    path('addresses/', views.address_list,name='address_list'),
    path('addresses/new/',views.address_add,name='address_add'),
    path('addresses/change/<int:pk>/',views.address_edit,name='address_edit'),
    path('addresses/delete/<int:pk>/',views.address_delete,name='address_delete'),
    path("addresses/default/<int:pk>/", views.address_set_default, name="address_set_default"),

]