from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from accounts.models import User


@shared_task
def send_email(user_id, mail_subject, message):
    try:
        user = User.objects.get(pk=user_id)

        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        pass
