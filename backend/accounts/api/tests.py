import threading
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connections
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.api.factories import AccountFactory
from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account
from balances.api.factories import BalanceRecordFactory
from balances.models import BalanceRecord
from core.api.tests import MOCK_RATES, BaseAPITest
from transactions.constants import TransactionType
from transactions.models import Transaction
from users.models import User


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
            "credit_limit",
            "latest_balance",
            "is_active",
            "created_at",
            "updated_at",
        }
        for field in required_fields:
            self.assertIn(field, resp.data["results"][0])

    def test_retrieve_accounts_latest_balance_calculation(self):
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
                self.assertEqual(Decimal(account_data["latest_balance"]), Decimal(100))
            elif account_data["id"] == account2.id:
                self.assertEqual(Decimal(account_data["latest_balance"]), Decimal(50))

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

    def test_autocomplete_accounts(self):
        accounts_count = 5
        AccountFactory.create_batch(accounts_count, user=self.user)
        url = reverse("account-autocomplete")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], accounts_count)
        required_fields = {"id", "name", "currency"}
        for field in required_fields:
            self.assertIn(field, resp.data["results"][0])

    def test_convert_latest_balance_uan_usd(self):
        with patch("accounts.api.views.get_exchange_rates", return_value=MOCK_RATES):
            uan_account = AccountFactory.create(user=self.user, currency=AccountCurrency.UAH)
            BalanceRecordFactory.create(account=uan_account, date=timezone.localdate(), amount=10000)
            url = reverse("account-list") + "?convert_to=USD"
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        account = resp.data["results"][0]
        self.assertEqual(account["id"], uan_account.id)
        self.assertEqual(Decimal(account["latest_balance"]), Decimal("225.05"))

    def test_convert_latest_balance_uan_eur(self):
        with patch("accounts.api.views.get_exchange_rates", return_value=MOCK_RATES):
            uan_account = AccountFactory.create(user=self.user, currency=AccountCurrency.UAH)
            BalanceRecordFactory.create(account=uan_account, date=timezone.localdate(), amount=10000)
            url = reverse("account-list") + "?convert_to=EUR"
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        account = resp.data["results"][0]
        self.assertEqual(account["id"], uan_account.id)
        self.assertEqual(Decimal(account["latest_balance"]), Decimal("193.05"))

    def test_convert_latest_balance_eur_usd(self):
        with patch("accounts.api.views.get_exchange_rates", return_value=MOCK_RATES):
            eur_account = AccountFactory.create(user=self.user, currency=AccountCurrency.EUR)
            BalanceRecordFactory.create(account=eur_account, date=timezone.localdate(), amount=100)
            url = reverse("account-list") + "?convert_to=USD"
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        account = resp.data["results"][0]
        self.assertEqual(account["id"], eur_account.id)
        self.assertEqual(Decimal(account["latest_balance"]), Decimal("115.34"))

    def test_convert_latest_balance_no_rates_returns_503(self):
        with patch("accounts.api.views.get_exchange_rates", return_value=[]):
            uan_account = AccountFactory.create(user=self.user, currency=AccountCurrency.UAH)
            BalanceRecordFactory.create(account=uan_account, date=timezone.localdate(), amount=10000)
            url = reverse("account-list") + "?convert_to=USD"
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 503)

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

    def test_create_account_without_type_and_category(self):
        url = reverse("account-list")
        data = {
            "name": "Test Account",
            "type": AccountType.ASSET,
            "currency": AccountCurrency.USD,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 400)
        data = {
            "name": "Test Account",
            "category": AccountCategory.CASH,
            "currency": AccountCurrency.USD,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 400)

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

    def test_create_credit_card_without_credit_limit(self):
        url = reverse("account-list")
        data = {
            "name": "Credit Card Account",
            "type": AccountType.LIABILITY,
            "category": AccountCategory.CREDIT_CARD,
            "currency": AccountCurrency.USD,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 400)

    def test_create_non_credit_card_with_credit_limit(self):
        url = reverse("account-list")
        data = {
            "name": "Non Credit Card Account",
            "type": AccountType.ASSET,
            "category": AccountCategory.CASH,
            "currency": AccountCurrency.USD,
            "credit_limit": 1000,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 201)
        account = Account.objects.get(name=data["name"], user=self.user)
        self.assertIsNone(account.credit_limit)

    def test_create_credit_card_with_credit_limit(self):
        url = reverse("account-list")
        data = {
            "name": "Credit Card Account",
            "type": AccountType.LIABILITY,
            "category": AccountCategory.CREDIT_CARD,
            "currency": AccountCurrency.USD,
            "credit_limit": 5000,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 201)
        account = Account.objects.get(name=data["name"], user=self.user)
        self.assertEqual(account.credit_limit, Decimal(5000))

    def test_update_credit_card_without_credit_limit(self):
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.CREDIT_CARD,
            credit_limit=1000,
        )
        url = reverse("account-detail", args=(account.id,))
        data = {
            "name": "New name",
        }
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.credit_limit, Decimal(1000))
        self.assertEqual(account.name, data["name"])

    def test_update_account_category_to_credit_card_without_credit_limit(self):
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
        )
        url = reverse("account-detail", args=(account.id,))
        data = {
            "type": AccountType.LIABILITY,
            "category": AccountCategory.CREDIT_CARD,
        }
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 400)
        account.refresh_from_db()
        self.assertEqual(account.category, AccountCategory.CASH)

    def test_update_account_category_to_another_category_with_credit_limit(self):
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.CREDIT_CARD,
            credit_limit=1000,
        )
        url = reverse("account-detail", args=(account.id,))
        data = {
            "category": AccountCategory.LOAN,
        }
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.category, AccountCategory.LOAN)
        self.assertIsNone(account.credit_limit)

    def test_update_credit_limit(self):
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.CREDIT_CARD,
            credit_limit=1000,
        )
        url = reverse("account-detail", args=(account.id,))
        data = {
            "credit_limit": 2000,
        }
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.credit_limit, Decimal(2000))

    def test_update_account_all_fields(self):
        account = AccountFactory.create(user=self.user)
        url = reverse("account-detail", args=(account.id,))
        data = {
            "name": "Updated Account",
            "type": AccountType.ASSET,
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
        account = AccountFactory.create(user=self.user, type=AccountType.LIABILITY, category=AccountCategory.MORTGAGE)
        url = reverse("account-detail", args=(account.id,))
        data = {"type": AccountType.ASSET, "category": AccountCategory.CASH}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.type, data["type"])
        self.assertEqual(account.category, data["category"])

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
        data = {"currency": AccountCurrency.EUR}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.currency, data["currency"])

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
        account = AccountFactory.create(
            user=self.user, type=AccountType.ASSET, category=AccountCategory.CASH, currency=AccountCurrency.USD
        )
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

    def test_create_account_with_invalid_type_category_combination(self):
        url = reverse("account-list")
        data = {
            "name": "Bad Combo",
            "type": AccountType.ASSET,
            "category": AccountCategory.CREDIT_CARD,
            "currency": AccountCurrency.USD,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 400)

    def test_create_account_with_valid_type_category_combinations(self):
        url = reverse("account-list")
        valid_combos = [
            (AccountType.ASSET, AccountCategory.CASH),
            (AccountType.ASSET, AccountCategory.INVESTMENTS),
            (AccountType.LIABILITY, AccountCategory.LOAN),
            (AccountType.LIABILITY, AccountCategory.MORTGAGE),
            (AccountType.EQUITY, AccountCategory.OTHER),
        ]
        for i, (account_type, account_category) in enumerate(valid_combos):
            data = {
                "name": f"Account {i}",
                "type": account_type,
                "category": account_category,
                "currency": AccountCurrency.USD,
            }
            resp = self.client.post(url, data)
            self.assertEqual(resp.status_code, 201, msg=f"Expected 201 for {account_type}/{account_category}")

    def test_update_account_category_incompatible_with_type(self):
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
        )
        url = reverse("account-detail", args=(account.id,))
        data = {"category": AccountCategory.LOAN}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 400)
        account.refresh_from_db()
        self.assertEqual(account.category, AccountCategory.CASH)

    def test_update_account_type_makes_category_invalid(self):
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.LOAN,
        )
        url = reverse("account-detail", args=(account.id,))
        data = {"type": AccountType.EQUITY}
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, 400)
        account.refresh_from_db()
        self.assertEqual(account.type, AccountType.LIABILITY)


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
        self.assertIsNotNone(income.import_fingerprint)

        expense = Transaction.objects.get(account=self.account, type=TransactionType.EXPENSE)
        self.assertEqual(expense.amount, Decimal("50.00"))
        self.assertEqual(expense.date, date(2026, 4, 23))
        self.assertEqual(expense.description, "Coffee")
        self.assertEqual(expense.raw_category, "Food")
        self.assertIsNotNone(expense.import_fingerprint)

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

    def test_import_duplicate_file(self):
        file = self._make_csv(
            "22.04.2026 10:00:00,Salary,1000.00,Electronics",
        )
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["imported"], 1)
        file.seek(0)
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 1)

    def test_import_duplicate_transaction_rows_in_different_files(self):
        file = self._make_csv(
            "22.04.2026 10:00:00,Salary,1000.00,Electronics",
        )
        file2 = self._make_csv(
            "22.04.2026 10:00:00,Salary,1000.00,Electronics",
            "22.04.2026 10:00:00,Salary,1000.00,Test",
        )
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["imported"], 1)
        resp = self.client.post(self.url, {"file": file2}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["imported"], 1)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 2)

    def test_import_duplicate_transaction_rows_in_same_file(self):
        file = self._make_csv(
            "22.04.2026 10:00:00,Salary,1000.00,Electronics",
            "22.04.2026 10:00:00,Salary,1000.00,Electronics",
        )
        resp = self.client.post(self.url, {"file": file}, format="multipart")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["imported"], 1)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 1)

    def test_concurrent_imports(self):
        file1 = self._make_csv(
            "22.04.2026 10:00:00,Salary,1000.00,Electronics",
        )
        file2 = self._make_csv(
            "23.04.2026 12:00:00,Coffee,-50.00,Food",
        )
        resp1 = self.client.post(self.url, {"file": file1}, format="multipart")
        resp2 = self.client.post(self.url, {"file": file2}, format="multipart")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp1.data["imported"], 1)
        self.assertEqual(resp2.data["imported"], 1)
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 2)


class ConcurrentImportRegressionTests(TransactionTestCase):
    """Regression: two threads submitting the same file must not both succeed.

    Uses TransactionTestCase (no wrapping savepoint) so each thread opens an
    independent DB connection and actually contends on the account row lock.
    """

    CSV_HEADER = "Date and time,Description,Amount,Category"
    client_class = APIClient

    def setUp(self):
        self.user = User.objects.create_user(
            email="concurrent@test.com",
            password="qwerty123456",
            name="Concurrent User",
        )
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])
        token = AccessToken.for_user(self.user)
        self.auth_header = f"Bearer {token}"
        self.account = AccountFactory.create(user=self.user)
        self.url = reverse("account-import-transaction", args=(self.account.id,))

    def _make_csv(self, *rows):
        content = "\n".join([self.CSV_HEADER, *rows]).encode("utf-8")
        return SimpleUploadedFile("transactions.csv", content, content_type="text/csv")

    def test_concurrent_imports_same_file_only_one_succeeds(self):
        statuses = []
        errors = []
        barrier = threading.Barrier(2)

        def do_import():
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=self.auth_header)
            file = self._make_csv("22.04.2026 10:00:00,Salary,1000.00,Electronics")
            barrier.wait()
            try:
                resp = client.post(self.url, {"file": file}, format="multipart")
                statuses.append(resp.status_code)
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)
            finally:
                connections.close_all()

        threads = [threading.Thread(target=do_import) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertEqual(
            sorted(statuses),
            [200, 400],
        )
        self.assertEqual(Transaction.objects.filter(account=self.account).count(), 1)
