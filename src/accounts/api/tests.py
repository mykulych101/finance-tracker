from django.urls import reverse

from accounts.api.factories import AccountFactory
from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account
from core.tests import BaseAPITest


class AccountTests(BaseAPITest):
    def setUp(self):
        self.user = self.create_and_login()

    def test_retrieve_accounts(self):
        accounts_count = 5
        AccountFactory.create_batch(accounts_count, user=self.user)
        url = reverse("account-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], accounts_count)
        required_fields = {"id", "name", "type", "category", "currency", "is_active", "created_at", "updated_at"}
        for field in required_fields:
            self.assertIn(field, resp.data["results"][0])

    def test_create_account(self):
        url = reverse("account-list")
        data = {
            "name": "Test Account",
            "type": AccountType.ASSET,
            "category": AccountCategory.CASH,
            "currency": AccountCurrency.USD,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 201)
        account = Account.objects.get(name=data["name"], user=self.user)
        self.assertEqual(account.type, data["type"])
        self.assertEqual(account.category, data["category"])
        self.assertEqual(account.currency, data["currency"])

    def test_create_duplicate_account_name(self):
        existing_account = AccountFactory.create(name="Existing", user=self.user)
        url = reverse("account-list")
        data = {
            "name": existing_account.name,
            "type": AccountType.ASSET,
            "category": AccountCategory.CASH,
            "currency": AccountCurrency.USD,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 400)
