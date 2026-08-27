from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

account_activation_token = PasswordResetTokenGenerator()


def build_activation_url(user) -> str:
    """Frontend URL that activates `user`'s account."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    return f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
