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