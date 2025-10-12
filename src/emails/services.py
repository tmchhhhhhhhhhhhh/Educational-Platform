from .models import Email, EmailVerification
from django.conf import settings
from django.core.mail import send_mail
import datetime
from django.utils import timezone
from datetime import timedelta

EMAIL_HOST_USER = settings.EMAIL_HOST_USER


def verify_email(email):
    qs = Email.objects.filter(email=email, active=False)
    return qs.exists


def get_verification_email_msg(verification_instance, as_html=False):
    if not isinstance(verification_instance, EmailVerification):
        return None
    verify_link = verification_instance.get_link()
    print(verify_link)
    if as_html:
        return f"<h1>Подтвердите вашу почту, перейдя по следующей ссылке:</h1><p><a href='{verify_link}'</a>{verify_link}</p>"
    return f"Подтвердите вашу почту, перейдя по следующей ссылке:\n{verify_link}"


def start_verification_event(email):
    email_obj, created = Email.objects.get_or_create(email=email)
    expiry = timezone.now() + timedelta(hours=1)
    obj = EmailVerification.objects.create(
        parent=email_obj,
        email=email,
        expired_at=expiry,
    )
    
    sent = send_verification_email(verify_obj=obj)
    return obj, sent


def send_verification_email(verify_obj):
    email = verify_obj.email
    subject = "Подтвердите почту"
    text_msg = get_verification_email_msg(verify_obj, as_html=False)
    text_html = get_verification_email_msg(verify_obj, as_html=True)
    from_user = EMAIL_HOST_USER
    to_user = email
    did_send = send_mail(
        subject,
        text_msg,
        from_user,
        [to_user],
        fail_silently=False,
        html_message=text_html,
    )
    return did_send

def verify_token(token, max_attemps=5):
    qs = EmailVerification.objects.filter(token=token)
    if not qs.exists() and not qs.count == 1:
        return False, "Неверный токен", None
    has_email_expired = qs.filter(expired=True)
    if has_email_expired.exists() or qs.expired_at < datetime.utcnow():
        return False, "Токен истёк, попробуйте снова.", None
    
    max_attemps_reached = qs.filter(attempts__gte=max_attemps)
    if max_attemps_reached.exists():
        #max_attemps_reached.update()
        return False, "Токен истёк, использовался много раз.", None
    obj = qs.first()
    obj.attempts +=1
    obj.last_attempt_at = timezone.now()
    if obj.attempts > max_attemps:
        obj.expired = True
        obj.expired_at = timezone.now()
    obj.save()
    email_obj = obj.parent
    return True, "Добро пожаловать!", email_obj