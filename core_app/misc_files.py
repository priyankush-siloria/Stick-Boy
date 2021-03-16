import string, random, datetime
from django.core.mail import send_mail
from django.conf import settings


def send_forgot_password_link(username, token, to):
    subject = "Forgot Password Link"
    html_content = f"""
    Hey {username},\n
    Click on this link for forgot password\n\n
    {settings.BASE_URL}create_new_password?token={token}
    """
    try:
        send_mail(subject=subject, message=html_content, from_email=settings.EMAIL_FROM, recipient_list=[to], fail_silently=False)
        return True
    except Exception:
        return False
