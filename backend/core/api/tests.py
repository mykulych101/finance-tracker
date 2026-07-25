from django.db.models import TextChoices
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
    client_class: CustomClient = CustomClient
    user = None
    client: CustomClient = None


class BaseAPITest(BaseTestCase, APITestCase):
    def create(self, email="test@mail.com", password="qwerty123456", name="John Snow"):  # noqa: S107
        user: User = User.objects.create_user(
            email=email,
            password=password,
            name=name,
        )
        user.is_active = True
        user.save(update_fields=["is_active"])

        return user

    def create_and_login(self, email="test@mail.com", password="qwerty123456", name="John Snow"):  # noqa: S107
        user: User = self.create(email=email, password=password, name=name)
        self.authorize(user)
        return user

    def authorize(self, user, **additional_headers):
        token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"{api_settings.AUTH_HEADER_TYPES[0]} {token}", **additional_headers)
