import random
from django.utils import timezone
from django.core.mail import send_mail

def send_otp(user):
    otp = str(random.randint(100000,999999))
    user.otp = otp
    user.otp_created = timezone.now()
    user.save()

    subject = "Your SmashStrix Verification OTP"
    message = f'Hello {user.first_name} , \n\n Your SmashStrix OTP for verification is {otp}. \n This will expire in 5 minutes.\n Thank You,\nSmashStrix Team'
    
    send_mail(subject,message,'Smashstrix <no-reply@smashstrix.com>',[user.email],fail_silently=False)

def send_reset_password_otp(user):
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_created = timezone.now()
    user.save()

    subject = "Reset Your SmashStrix Password"

    message = (
        f"Hello {user.first_name},\n\n"
        f"We received a request to reset your SmashStrix account password.\n"
        f"Your OTP for password reset is: {otp}\n\n"
        f"This OTP will expire in 5 minutes.\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Thank You,\nSmashStrix Team"
    )

    send_mail(subject,message,"SmashStrix <no-reply@smashstrix.com>",[user.email],fail_silently=False)

def send_email_change_otp(user):
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_created = timezone.now()
    user.otp_verified = False
    user.save(update_fields=["otp", "otp_created", "otp_verified"])

    send_mail(
        subject="Verify your new email - SmashStrix",
        message=f"Hello {user.first_name}, \n\n Your OTP for email verification is {otp}. It expires in 5 minutes.",
        from_email="SmashStrix <no-reply@smashstrix.com>",
        recipient_list=[user.pending_email],
        fail_silently=False,
    )
