from django.core.mail import send_mail
from frontwall.settings import EMAIL_HOST_USER
import random

def send_otp(sub,username,email,action):
    s = ''
    for i in range(6):
        s+= str(random.randint(0,9))

    otp = s
    msg = f'Hey {username},\nYour OTP for {action} is\n{otp}\nThank You,\nTeam Frontwall'
    send_mail(sub,msg,EMAIL_HOST_USER,[email],fail_silently=False)
    return otp
