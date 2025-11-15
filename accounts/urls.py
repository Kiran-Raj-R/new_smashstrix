from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.user_signup,name='signup'),
    path('login/',views.user_login,name='login'),
    path('profile/',views.user_profile,name='profile'),
    path('logout/',views.user_logout,name='logout'),
    path('verify-otp/',views.verify_otp,name='verify_otp'),
    path('resend-otp/',views.resend_otp,name='resend_otp'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('forgot-password-otp/',views.forgot_password_otp,name='forgot_password_otp'),
    path('password-reset/',views.password_reset,name='password_reset'),
]