from django.core.mail import send_mail
from django.conf import settings
from decouple import config

EMAIL_HOST_USER = config("EMAIL_HOST_USER", cast=str, default=None)


print("hello")
send_mail(
    subject="Test email",
    message="Ассаламу алейкум! Это тестовое письмо от Django 💌",
    from_email=EMAIL_HOST_USER,
    recipient_list=["tvoydid@gmail.com", "stevehilenberg@gmail.com"],
)
print(EMAIL_HOST_USER)
print("hello")
"""
    EMAIL_HOST = config("EMAIL_HOST", cast=str, default=None)

EMAIL_PORT = config("EMAIL_PORT", cast=str, default="587")

EMAIL_HOST_USER = config("EMAIL_HOST_USER", cast=str, default=None)

EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", cast=str, default=None)

EMAIL_USE_TLS = config(
    "EMAIL_USE_TLS", cast=bool, default=True
)  # Use EMAIL_PORT 587 for TLS


    """
