import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email(self, subject: str, template: str, recipients: list, context: dict):
    """Render `template` with `context` and email it to `recipients`.

    Rendering happens here rather than at the call site so callers only have to
    hand over JSON-serializable data, which is all Celery can carry anyway.
    """
    message = render_to_string(template, context)
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
    except Exception:
        logger.exception("Failed to send %r to %s", subject, recipients)
        try:
            self.retry(countdown=60)
        except MaxRetriesExceededError:
            logger.exception("Giving up on %r to %s", subject, recipients)
