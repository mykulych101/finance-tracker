from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from accounts.api.factories import AccountFactory
from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account
from balances.api.factories import BalanceRecordFactory
from balances.models import BalanceRecord
from core.api.tests import BaseAPITest
from transactions.constants import TransactionType
from transactions.models import Transaction


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
        required_fields = {
            "id",
            "name",
            "type",
            "category",
            "currency",
            "current_balance",
            "is_active",
            "created_at",
            "updated_at",
        }
        for field in required_fields:
            self.assertIn(field, resp.data["results"][0])

    def test_retrieve_accounts_current_balance_calculation(self):
        today = timezone.localdate()
        yesterday = today - timezone.timedelta(days=1)
        account1 = AccountFactory.create(user=self.user)
        account2 = AccountFactory.create(user=self.user)
        BalanceRecordFactory.create(account=account1, date=today, amount=100)
        BalanceRecordFactory.create(account=account2, date=yesterday, amount=50)
        url = reverse("account-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        for account_data in resp.data["results"]:
            if account_data["id"] == account1.id:
                self.assertEqual(account_data["current_balance"], 100)
            elif account_data["id"] == account2.id:
                self.assertEqual(account_data["current_balance"], 50)

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

        existing_account.is_active = False
        existing_account.save(update_fields=["is_active"])
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 201)

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

    def test_update_account_with_same_name(self):
        account = AccountFactory.create(name="Same Name", user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {"name": "Same Name"}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.name, data["name"])

    def test_update_account_type(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {"type": AccountType.ASSET}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.type, data["type"])

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


class ImportTransactionTests(BaseAPITest):
    CSV_HEADER = "Date and time,Description,Amount,Category"

    def setUp(self):
        self.user = self.create_and_login()
        self.account = AccountFactory.create(user=self.user)
        self.url = reverse("account-import-transaction", args=(self.account.id,))

    def _make_csv(self, *rows):
        content = "\n".join([self.CSV_HEADER, *rows]).encode("utf-8")
        return SimpleUploadedFile("transactions.csv", content, content_type="text/csv")

    def test_import_success(self):
        file = self._make_csv(
            "22.04.2026 10:00:00,Salary,1000.00,Electronics",
            "23.04.2026 12:00:00,Coffee,-50.00,Food",
        )
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["imported"], 2)

        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 2)

        income = Transaction.objects.get(account=self.account, type=TransactionType.INCOME)
        self.assertEqual(income.amount, Decimal("1000.00"))
        self.assertEqual(income.description, "Salary")
        self.assertEqual(income.date, date(2026, 4, 22))
        self.assertEqual(income.raw_category, "Electronics")

        expense = Transaction.objects.get(account=self.account, type=TransactionType.EXPENSE)
        self.assertEqual(expense.amount, Decimal("50.00"))
        self.assertEqual(expense.date, date(2026, 4, 23))
        self.assertEqual(expense.description, "Coffee")
        self.assertEqual(expense.raw_category, "Food")

        balance_record = BalanceRecord.objects.filter(account=self.account).first()
        self.assertIsNotNone(balance_record)
        self.assertEqual(balance_record.amount, Decimal("950.00"))
        self.assertEqual(balance_record.date, date(2026, 4, 23))

    def test_import_missing_amount(self):
        file = self._make_csv("01.01.2026 10:00:00,Salary,,Electronics")
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 0)

    def test_import_missing_date(self):
        file = self._make_csv(",Salary,1000.00,Electronics")
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 0)

    def test_import_invalid_date(self):
        file = self._make_csv("not-a-date,Salary,1000.00,Electronics")
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 0)
