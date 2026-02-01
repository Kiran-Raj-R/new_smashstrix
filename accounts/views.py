from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login,logout,get_user_model
from django.utils import timezone
from . models import User
from . utils import send_otp, send_reset_password_otp
from . forms import UserSignupForm, UserloginForm

User = get_user_model()

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UserSignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        send_otp(user)
        request.session['pending_user'] = user.id
        messages.info(request,"An OTP has been send to your email. Please verify.")
        return redirect('verify_otp')
    return render(request,'accounts/signup.html',{'form':form})

def verify_otp(request):
    user_id = request.session.get('pending_user')
    if not user_id:
        return redirect('signup')
    user = User.objects.get(id=user_id)

    remaining_seconds = 0
    if user.otp_created:
        expiry_time = user.otp_created + timezone.timedelta(minutes=5)
        remaining_seconds = max(int((expiry_time - timezone.now()).total_seconds()), 0)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if user.otp == entered_otp and not user.otp_expired():
            user.is_active = True
            user.otp_verified = True
            user.otp = None
            user.save()
            del request.session['pending_user']
            messages.success(request,"Account verified Successfully. You can now login to Smashstrix.")
            return redirect('login')
        else:
            messages.error(request,"Invalid OTP or OTP expired..")
            return redirect('verify_otp')
    return render(request,'accounts/otp_verify.html',{'user':user, 'remaining_seconds':remaining_seconds})

def resend_otp(request):
    user_id = request.session.get('pending_user')
    if not user_id:
        return redirect('signup')
    user = User.objects.get(id=user_id)
    send_otp(user)
    messages.success(request,"A new otp has been sent to your email...")
    return redirect('verify_otp')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = UserloginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data["user"]
        login(request,user)
        messages.success(request,'Welcome to Smashstrix.')
        return redirect('home')
    return render(request,'accounts/login.html',{'form':form})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            send_reset_password_otp(user)
            request.session['reset_user'] = user.id
            messages.success(request,"An OTP has been sent to your registered mail")
            return redirect('forgot_password_otp')
        except User.DoesNotExist:
            messages.error(request,"User does not exist with the given email address")
    return render(request,'accounts/forgot_password.html')

def forgot_password_otp(request):
    user_id = request.session.get('reset_user')
    if not user_id:
        return redirect('forgot_password')
    
    user = User.objects.get(id=user_id)

    remaining_seconds = 0
    if user.otp_created:
        expiry_time = user.otp_created + timezone.timedelta(minutes=5)
        remaining_seconds = max(int((expiry_time - timezone.now()).total_seconds()), 0)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if user.otp == entered_otp and not user.otp_expired():
            messages.success(request,"OTP verified! You can reset your password now.")
            return redirect('password_reset')
        else:
            messages.error(request,"Invalid or expired OTP")
            return redirect('forgot_password_otp')
    return render(request,'accounts/forgot_password_otp.html',{'user':user, 'remaining_seconds': remaining_seconds})

def password_reset(request):
    user_id = request.session.get('reset_user')
    if not user_id:
        return redirect('forgot_password')
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not password1 or not password2:
            messages.error(request, "Password fields cannot be empty.")
            return redirect('password_reset')
        
        if len(password1) < 8:
            messages.error(request,"Password must contain at least 8 characters.")
            return redirect('password_reset')

        if password1 != password2:
            messages.error(request,"The passwords doesn't match..")
            return redirect('password_reset')
        
        user.set_password(password1)
        user.otp = None
        user.otp_created = None
        user.otp_verified = False

        user.save(update_fields=[
            'password', 'otp', 'otp_created', 'otp_verified'
        ])

        request.session.pop('reset_user', None)
        messages.success(request,"Password reset successfully.")
        return redirect('login')

    return render(request,'accounts/password_reset.html')

def user_logout(request):
    logout(request)
    request.session.flush()
    messages.success(request,"You have logged out successfully.")
    return redirect('home')
