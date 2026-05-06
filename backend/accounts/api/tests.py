from django.urls import reverse

from accounts.api.factories import AccountFactory
from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account
from core.api.tests import BaseAPITest


class AccountTests(BaseAPITest):
    def setUp(self):
        self.user = self.create_and_login()

    def test_retrieve_accounts(self):
        accounts_count = 5
        another_user = self.create(email="test2@mail.com", password="qwerty123456", name="John Snow 2")
        AccountFactory.create_batch(accounts_count, user=self.user)
        AccountFactory.create_batch(accounts_count, user=another_user)
        inactive_account = Account.objects.filter(user=self.user).first()
        inactive_account.is_active = False
        inactive_account.save(update_fields=["is_active"])
        url = reverse("account-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], accounts_count - 1)
        required_fields = {"id", "name", "type", "category", "currency", "is_active", "created_at", "updated_at"}
        for field in required_fields:
            self.assertIn(field, resp.data["results"][0])

    def test_retrieve_account_by_id(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], account.id)
        self.assertEqual(resp.data["name"], account.name)
        self.assertEqual(resp.data["type"], account.type)
        self.assertEqual(resp.data["category"], account.category)
        self.assertEqual(resp.data["currency"], account.currency)

    def test_retrieve_non_active_account_by_id(self):
        account = AccountFactory.create(user=self.user, is_active=False)
        url = reverse("account-detail", args=(account.id,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

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

    def test_update_account_all_fields(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {
            "name": "Updated Account",
            "type": AccountType.LIABILITY,
            "category": AccountCategory.INVESTMENTS,
            "currency": AccountCurrency.EUR,
        }
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.name, data["name"])
        self.assertEqual(account.type, data["type"])
        self.assertEqual(account.category, data["category"])
        self.assertEqual(account.currency, data["currency"])

    def test_update_account_duplicate_name(self):
        account = AccountFactory.create(user=self.user)
        AccountFactory.create(name="Updated Account", user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {"name": "Updated Account"}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 400)

    def test_update_account_minimal_payload(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {"type": AccountType.EQUITY}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.type, data["type"])

    def test_update_account_empty_payload(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        resp = self.client.patch(url, {})
        self.assertEqual(resp.status_code, 200)

    def test_update_account_invalid_payload(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {"type": "invalid"}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 400)

    def test_update_non_existing_account(self):
        url = reverse("account-detail", args=(999,))
        data = {"name": "Non-existing"}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 404)

    def test_update_account_of_another_user(self):
        another_user = self.create(email="test2@test.com", password="qwerty123456", name="John Snow 2")
        account_of_another_user = AccountFactory.create(user=another_user)
        url = reverse("account-detail", args=(account_of_another_user.id,))
        data = {"name": "Hacked Account"}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 404)

    def test_update_non_active_account(self):
        non_active_account = AccountFactory.create(user=self.user, is_active=False)
        url = reverse("account-detail", args=(non_active_account.id,))
        data = {"name": "Hacked Account"}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 404)

    def test_update_account_read_only_fields(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {"created_at": "2020-01-01T00:00:00Z", "updated_at": "2020-01-01T00:00:00Z", "is_active": False}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertNotEqual(account.created_at.isoformat(), data["created_at"])
        self.assertNotEqual(account.updated_at.isoformat(), data["updated_at"])
        self.assertNotEqual(account.is_active, data["is_active"])

    def test_soft_delete_account(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        account.refresh_from_db()
        self.assertFalse(account.is_active)
