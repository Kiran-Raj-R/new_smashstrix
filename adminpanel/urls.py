from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.admin_login,name='admin_login'),
    path("logout/", views.admin_logout, name="admin_logout"),
    path('',views.admin_dashboard,name='admin_dashboard'),

    path("users/", views.admin_user_list, name="admin_users"),
    path("users/block/<int:user_id>/", views.block_user, name="admin_block_user"),
    path("users/unblock/<int:user_id>/", views.unblock_user, name="admin_unblock_user"),

    path('brands/',views.brand_list,name='admin_brands'),
    path('brands/new/',views.brand_add,name='admin_brand_add'),
    path('brands/change/<int:pk>/',views.brand_edit,name='admin_brand_edit'),
    path('brands/delete/<int:pk>/',views.brand_delete,name='admin_brand_delete'),

    path('categories/',views.category_list,name='admin_categories'),
    path('categories/new/',views.category_add,name='admin_category_add'),
    path('categories/change/<int:pk>/',views.category_edit,name='admin_category_edit'),
    path('categories/delete/<int:pk>/',views.category_delete,name='admin_category_delete'),

    path('products/', views.product_list, name='admin_products'),
    path('products/new/',views.product_add,name='admin_product_add'),
    path("products/change/<int:product_id>/", views.product_edit, name="admin_product_edit"),
    path('products/delete/<int:pk>/', views.product_delete, name='admin_product_delete'),
    
    path("products/image/delete/<int:img_id>/", views.product_image_delete,name="admin_product_image_delete"),
    path("products/<int:product_id>/color/new/", views.color_variant_add,name="admin_color_variant_add"),
    path("products/color/delete/<int:variant_id>/", views.color_variant_delete,name="admin_color_variant_delete"),
]