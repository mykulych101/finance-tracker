from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", password="testpass123", name="Test User")
        self.url = reverse("accounts_api:profile")
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["name"], self.user.name)

    def test_update_profile(self):
        data = {"name": "Updated Name"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Updated Name")
