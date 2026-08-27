from django.db.models import TextChoices
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User

MOCK_RATES = [
    {
        "currencyCodeA": 840,
        "currencyCodeB": 980,
        "date": 1552392228,
        "rateBuy": 44.04,
        "rateSell": 44.4346,
        "rateCross": None,
    },
    {
        "currencyCodeA": 978,
        "currencyCodeB": 980,
        "date": 1552392228,
        "rateBuy": 51.25,
        "rateSell": 51.8001,
        "rateCross": None,
    },
]


class Colors(TextChoices):
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class CustomClient(APIClient):
    format = "json"

    def get(self, path, data=None, **extra) -> Response:
        print(f"{Colors.BOLD}{Colors.WARNING} GET:{Colors.END} {path}")  # noqa: T201
        return super().get(path, data=data, **extra)

    def put(self, path, data=None, **extra) -> Response:
        print(f"{Colors.BOLD}{Colors.WARNING} PUT:{Colors.END} {path}")  # noqa: T201
        return super().put(path, data=data, **extra)

    def patch(self, path, data=None, **extra) -> Response:
        print(f"{Colors.BOLD}{Colors.WARNING} PATCH:{Colors.END} {path}")  # noqa: T201
        return super().patch(path, data=data, **extra)

    def delete(self, path, data=None, **extra) -> Response:
        print(f"{Colors.BOLD}{Colors.WARNING} DELETE:{Colors.END} {path}")  # noqa: T201
        return super().delete(path, data=data, **extra)

    def post(self, path, data=None, **extra) -> Response:
        print(f"{Colors.BOLD}{Colors.WARNING} POST:{Colors.END} {path}")  # noqa: T201
        return super().post(path, data=data, **extra)


class BaseTestCase:
    client_class: type[APIClient] = CustomClient
    user = None


class BaseAPITest(BaseTestCase, APITestCase):
    def create(self, email="test@mail.com", password="qwerty123456", name="John Snow", is_verified=True):  # noqa: S107
        user: User = User.objects.create_user(
            email=email,
            password=password,
            name=name,
        )
        user.is_active = True
        user.is_verified = is_verified
        user.save(update_fields=["is_active", "is_verified"])

        return user

    def create_and_login(self, email="test@mail.com", password="qwerty123456", name="John Snow"):  # noqa: S107
        user: User = self.create(email=email, password=password, name=name)
        self.authorize(user)
        return user

    def authorize(self, user, **additional_headers):
        token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"{api_settings.AUTH_HEADER_TYPES[0]} {token}", **additional_headers)


class VerifiedPermissionTestMixin:
    """Assert one endpoint of an app sits behind the `IsVerified` default.

    Mixed into every app's own test module on purpose. A single shared test
    would keep passing if one app quietly slipped back to `AllowAny`, so each
    app carries its own copy of these three assertions.
    """

    gated_url_name = None

    def gated_url(self):
        return reverse(self.gated_url_name)

    def test_verified_user_passes_the_gate(self):
        self.create_and_login()

        response = self.client.get(self.gated_url())

        self.assertNotIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_unverified_user_is_rejected(self):
        self.authorize(self.create(is_verified=False))

        response = self.client.get(self.gated_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(str(response.data["detail"]), "Email is not verified.")

    def test_anonymous_user_is_rejected(self):
        response = self.client.get(self.gated_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
