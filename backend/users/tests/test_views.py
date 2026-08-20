from unittest.mock import patch

from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.utils import account_activation_token, build_activation_url


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users_api:register")
        self.payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "supersecret1",
        }

    @patch("users.api.views.send_email.delay")
    def test_register_creates_user(self, mock_send_email):
        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "john@example.com")
        self.assertNotIn("password", response.data)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

        user = User.objects.get(email="john@example.com")
        self.assertTrue(user.check_password("supersecret1"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)

        mock_send_email.assert_called_once()
        kwargs = mock_send_email.call_args.kwargs
        self.assertEqual(kwargs["subject"], "Activate your account")
        self.assertEqual(kwargs["template"], "email/activation_email.html")
        self.assertEqual(kwargs["recipients"], [user.email])
        self.assertEqual(kwargs["context"]["user_name"], user.name)
        self.assertEqual(kwargs["context"]["activation_link"], build_activation_url(user))

    @patch("users.api.views.send_email.delay")
    def test_register_rejects_short_password(self, mock_send_email):
        response = self.client.post(self.url, {**self.payload, "password": "short"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["password"],
            ["Ensure password field has at least 9 characters."],
        )
        self.assertFalse(User.objects.filter(email="john@example.com").exists())
        mock_send_email.assert_not_called()

    @patch("users.api.views.send_email.delay")
    def test_register_rejects_long_password(self, mock_send_email):
        response = self.client.post(self.url, {**self.payload, "password": "x" * 21})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["password"],
            ["Ensure password field has no more than 20 characters."],
        )
        mock_send_email.assert_not_called()

    @patch("users.api.views.send_email.delay")
    def test_register_rejects_duplicate_email(self, mock_send_email):
        User.objects.create_user(email="john@example.com", name="Existing", password="supersecret1")

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.filter(email="john@example.com").count(), 1)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users_api:login")
        self.user = User.objects.create_user(email="john@example.com", name="John Doe", password="supersecret1")

    def test_login_returns_tokens_for_verified_user(self):
        self.user.is_verified = True
        self.user.save()

        response = self.client.post(self.url, {"email": "john@example.com", "password": "supersecret1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_unverified_user(self):
        response = self.client.post(self.url, {"email": "john@example.com", "password": "supersecret1"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_rejects_wrong_password(self):
        self.user.is_verified = True
        self.user.save()

        response = self.client.post(self.url, {"email": "john@example.com", "password": "wrong-password"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users_api:logout")
        self.user = User.objects.create_user(email="john@example.com", name="John Doe", password="supersecret1")

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {"refresh": str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # A blacklisted refresh token can no longer be reused
        reuse = self.client.post(reverse("token_refresh"), {"refresh": str(refresh)})
        self.assertEqual(reuse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_refresh_returns_400(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_invalid_refresh_returns_400(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {"refresh": "not-a-token"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(self.url, {"refresh": str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users_api:change-password")
        self.user = User.objects.create_user(
            email="john@example.com", name="John Doe", password="supersecret1", is_verified=True
        )

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.put(
            self.url,
            {"old_password": "supersecret1", "new_password": "brand-new-pass1"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("brand-new-pass1"))

    def test_change_password_rejects_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.put(
            self.url,
            {"old_password": "wrong-password", "new_password": "brand-new-pass1"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["old_password"], ["Wrong password."])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("supersecret1"))

    def test_change_password_requires_both_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.put(self.url, {"old_password": "supersecret1"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_change_password_requires_authentication(self):
        response = self.client.put(
            self.url,
            {"old_password": "supersecret1", "new_password": "brand-new-pass1"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ActivateAccountViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="john@example.com", name="John Doe", password="supersecret1")
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

    def url_for(self, uidb64, token):
        return reverse("users_api:activate", kwargs={"uidb64": uidb64, "token": token})

    def test_activate_marks_user_verified(self):
        response = self.client.get(self.url_for(self.uidb64, self.token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_activate_rejects_invalid_token(self):
        response = self.client.get(self.url_for(self.uidb64, "invalid-token"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    def test_activate_rejects_unknown_user(self):
        unknown_uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk + 999))

        response = self.client.get(self.url_for(unknown_uidb64, self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_token_invalidated_by_password_change(self):
        self.user.set_password("brand-new-pass1")
        self.user.save()

        response = self.client.get(self.url_for(self.uidb64, self.token))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)


class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("users_api:profile")
        self.user = User.objects.create_user(
            email="john@example.com", name="John Doe", password="supersecret1", is_verified=True
        )

    def test_profile_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_current_user(self):
        other = User.objects.create_user(
            email="other@example.com", name="Other", password="supersecret1", is_verified=True
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertNotEqual(response.data["id"], other.id)

    def test_profile_email_is_read_only(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(self.url, {"email": "hacker@example.com", "name": "Renamed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "john@example.com")
        self.assertEqual(self.user.name, "Renamed")


class VerifiedPermissionTests(APITestCase):
    """How the IsVerified default plays out across this app's own endpoints.

    Each data app asserts its own gate via `VerifiedPermissionTestMixin`, so a
    single app slipping back to `AllowAny` fails that app's suite.
    """

    def setUp(self):
        self.user = User.objects.create_user(email="john@example.com", name="John Doe", password="supersecret1")

    def test_unverified_user_cannot_read_own_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("users_api:profile"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_user_can_logout(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse("users_api:logout"), {"refresh": str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unverified_user_cannot_change_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.put(
            reverse("users_api:change-password"),
            {"old_password": "supersecret1", "new_password": "brand-new-pass1"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("users.api.views.send_email.delay")
    def test_register_stays_public(self, mock_send_email):
        response = self.client.post(
            reverse("users_api:register"),
            {"name": "Jane Doe", "email": "jane@example.com", "password": "supersecret1"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_stays_public(self):
        self.user.is_verified = True
        self.user.save()

        response = self.client.post(
            reverse("users_api:login"),
            {"email": "john@example.com", "password": "supersecret1"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
