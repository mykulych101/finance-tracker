from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from accounts.api.factories import AccountFactory
from balances.api.factories import BalanceRecordFactory
from balances.models import BalanceRecord
from core.api.tests import BaseAPITest
from transactions.api.factories import TransactionFactory
from transactions.constants import TransactionType
from transactions.models import Transaction


class TransactionTests(BaseAPITest):
    def setUp(self):
        self.user = self.create_and_login()
        self.list_url = reverse("transactions-list")
        self.account = AccountFactory.create(user=self.user)
        self.other_user = self.create(email="test3@mail.com", password="qwerty123456", name="John Snow 3")
        self.other_user_account = AccountFactory.create(user=self.other_user)

    def test_retrieve_transactions(self):
        transactions_count = 5
        TransactionFactory.create_batch(transactions_count, account=self.account)
        TransactionFactory.create_batch(transactions_count, account=self.other_user_account)
        self.assertEqual(Transaction.objects.count(), transactions_count * 2)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], transactions_count)
        transaction = resp.data["results"][0]
        self.assertEqual(transaction["account"]["id"], self.account.id)
        self.assertEqual(transaction["account"]["name"], self.account.name)
        required_fields = {
            "id",
            "account",
            "type",
            "amount",
            "date",
            "description",
            "raw_category",
            "is_system",
            "created_at",
            "updated_at",
        }
        for field in required_fields:
            self.assertIn(field, transaction)

    def test_create__with_another_users_account(self):
        data = {
            "account_id": self.other_user_account.id,
            "type": TransactionType.INCOME,
            "amount": 100.0,
            "date": timezone.localdate().isoformat(),
            "description": "Test transaction",
            "raw_category": "Salary",
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_create__balance_record_exists_on_date(self):
        balance_records_count = 5
        # Prepare balance records before including the one on the transaction date
        for i in range(balance_records_count):
            BalanceRecordFactory.create(account=self.account, date=timezone.localdate() - timedelta(days=i), amount=100)
        # Prepare balance records after
        for i in range(balance_records_count):
            BalanceRecordFactory.create(
                account=self.account, date=timezone.localdate() + timedelta(days=i + 1), amount=100
            )
        balance_records_before = {br.id: br.amount for br in BalanceRecord.objects.all()}
        data = {
            "account_id": self.account.id,
            "type": TransactionType.EXPENSE,
            "amount": 50.0,
            "date": timezone.localdate().isoformat(),
            "description": "Test transaction",
            "raw_category": "Food",
        }
        with self.assertNumQueries(12):
            resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self._assert_transaction_fields(transaction, data)
        self._assert_balance_records_amounts(transaction, balance_records_before)

    def test_create__balance_record_exists_on_date__other_transactions_exist(self):
        balance_records_count = 5
        transactions_count = 3
        today = timezone.localdate()
        prev_day_amount = 100
        existing_transaction_amount = 10
        # Prepare balance records before today (not including today)
        for i in range(1, balance_records_count + 1):
            BalanceRecordFactory.create(account=self.account, date=today - timedelta(days=i), amount=prev_day_amount)
        # Prepare balance records after
        for i in range(balance_records_count):
            BalanceRecordFactory.create(account=self.account, date=today + timedelta(days=i + 1), amount=100)
        # Create existing transactions on today with a known type so the expected balance is deterministic
        TransactionFactory.create_batch(
            transactions_count,
            account=self.account,
            date=today,
            raw_category="Food",
            amount=existing_transaction_amount,
            type=TransactionType.INCOME,
        )
        # Today's balance must reflect previous day + existing transactions
        today_amount = prev_day_amount + transactions_count * existing_transaction_amount
        BalanceRecordFactory.create(account=self.account, date=today, amount=today_amount)
        balance_records_before = {br.id: br.amount for br in BalanceRecord.objects.all()}
        data = {
            "account_id": self.account.id,
            "type": TransactionType.EXPENSE,
            "amount": 50.0,
            "date": timezone.localdate().isoformat(),
            "description": "Test transaction",
            "raw_category": "Test",
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Transaction.objects.count(), transactions_count + 1)
        transaction = Transaction.objects.filter(raw_category="Test").first()
        self._assert_transaction_fields(transaction, data)
        self._assert_balance_records_amounts(transaction, balance_records_before)

    def test_create__no_balance_record_on_date(self):
        balance_records_count = 5
        for i in range(balance_records_count):
            BalanceRecordFactory.create(
                account=self.account, date=timezone.localdate() - timedelta(days=i + 1), amount=100
            )
        for i in range(balance_records_count):
            BalanceRecordFactory.create(
                account=self.account, date=timezone.localdate() + timedelta(days=i + 1), amount=100
            )
        balance_records_before = {br.id: br.amount for br in BalanceRecord.objects.all()}
        data = {
            "account_id": self.account.id,
            "type": TransactionType.EXPENSE,
            "amount": 50.0,
            "date": timezone.localdate().isoformat(),
            "description": "Test transaction",
            "raw_category": "Food",
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self._assert_transaction_fields(transaction, data)
        self._assert_balance_records_amounts(transaction, balance_records_before)

    def test_create__no_balance_record_on_date__no_previous_balance(self):
        balance_records_count = 5
        for i in range(balance_records_count):
            BalanceRecordFactory.create(
                account=self.account, date=timezone.localdate() + timedelta(days=i + 1), amount=100
            )
        balance_records_before = {br.id: br.amount for br in BalanceRecord.objects.all()}
        data = {
            "account_id": self.account.id,
            "type": TransactionType.INCOME,
            "amount": 100.0,
            "date": timezone.localdate().isoformat(),
            "description": "Test transaction",
            "raw_category": "Salary",
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self._assert_transaction_fields(transaction, data)
        self._assert_balance_records_amounts(transaction, balance_records_before)

    def test_create__no_balance_records_at_all(self):
        data = {
            "account_id": self.account.id,
            "type": TransactionType.INCOME,
            "amount": 100.0,
            "date": timezone.localdate().isoformat(),
            "description": "Test transaction",
            "raw_category": "Salary",
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self._assert_transaction_fields(transaction, data)
        balance_record = BalanceRecord.objects.filter(account=self.account, date=transaction.date).first()
        self.assertIsNotNone(balance_record)
        self.assertEqual(balance_record.amount, transaction.amount)
        self._assert_balance_records_amounts(transaction, balance_records_before={})

    def test_update__with_another_users_account(self):
        transaction = TransactionFactory.create(account=self.account)
        data = {
            "account_id": self.other_user_account.id,
            "type": TransactionType.INCOME,
            "amount": 100.0,
            "date": timezone.localdate().isoformat(),
            "description": "Test transaction",
            "raw_category": "Salary",
        }
        url = reverse("transactions-detail", args=[transaction.id])
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, 400)
        transaction.refresh_from_db()
        self.assertEqual(transaction.account, self.account)

    def test_update__balance_record_exists_on_date(self):
        today = timezone.localdate()
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        balance_record = BalanceRecordFactory.create(account=self.account, date=today, amount="100")

        url = reverse("transactions-detail", args=(transaction.id,))
        data = {
            "account_id": self.account.id,
            "type": TransactionType.EXPENSE,
            "amount": Decimal(50),
            "date": today.isoformat(),
            "description": "Updated transaction",
            "raw_category": "Updated category",
        }
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, 200)

        transaction.refresh_from_db()
        self._assert_transaction_fields(transaction, data)

        balance_record.refresh_from_db()
        # prev=0, income=0, expense=50 → -50
        self.assertEqual(balance_record.amount, Decimal(-50))

    def test_update__balance_record_exists_on_date__other_transactions_exist(self):
        today = timezone.localdate()
        prev_amount = "100"
        BalanceRecordFactory.create(account=self.account, date=today - timedelta(days=1), amount=prev_amount)

        existing_amount = "10"
        TransactionFactory.create_batch(
            2, account=self.account, date=today, amount=existing_amount, type=TransactionType.INCOME
        )
        transaction = TransactionFactory.create(
            account=self.account, date=today, amount=existing_amount, type=TransactionType.INCOME
        )
        # prev=100, 3x income=10 → today=130
        balance_record = BalanceRecordFactory.create(
            account=self.account, date=today, amount=prev_amount + 3 * existing_amount
        )

        url = reverse("transactions-detail", args=(transaction.id,))
        data = {
            "account_id": self.account.id,
            "type": TransactionType.EXPENSE,
            "amount": "20",
            "date": today.isoformat(),
            "description": "Updated transaction",
            "raw_category": "Updated category",
        }
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, 200)

        balance_record.refresh_from_db()
        # prev=100, income=10+10=20, expense=20 → 100
        self.assertEqual(balance_record.amount, Decimal(prev_amount))

    def test_update__subsequent_balances_updated(self):
        today = timezone.localdate()
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        balance_today = BalanceRecordFactory.create(account=self.account, date=today, amount="100")
        TransactionFactory.create(
            account=self.account, date=today + timedelta(days=1), amount=Decimal(50), type=TransactionType.INCOME
        )
        balance_tomorrow = BalanceRecordFactory.create(
            account=self.account, date=today + timedelta(days=1), amount=Decimal(150)
        )
        TransactionFactory.create(
            account=self.account, date=today + timedelta(days=2), amount=Decimal(20), type=TransactionType.EXPENSE
        )
        balance_day_after = BalanceRecordFactory.create(
            account=self.account, date=today + timedelta(days=2), amount=Decimal(130)
        )

        url = reverse("transactions-detail", args=(transaction.id,))
        data = {
            "account_id": self.account.id,
            "type": TransactionType.INCOME,
            "amount": Decimal(60),
            "date": today.isoformat(),
            "description": "Updated",
            "raw_category": "Updated",
        }
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, 200)

        balance_today.refresh_from_db()
        balance_tomorrow.refresh_from_db()
        balance_day_after.refresh_from_db()
        # net delta = 60 - 100 = -40 applied to all records from today onwards
        self.assertEqual(balance_today.amount, Decimal(60))
        self.assertEqual(balance_tomorrow.amount, Decimal(110))
        self.assertEqual(balance_day_after.amount, Decimal(90))

    def test_update__date_changed__to_future(self):
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        balance_today = BalanceRecordFactory.create(account=self.account, date=today, amount="100")

        url = reverse("transactions-detail", args=(transaction.id,))
        data = {
            "account_id": self.account.id,
            "type": TransactionType.INCOME,
            "amount": "100",
            "date": tomorrow.isoformat(),
            "description": "Updated",
            "raw_category": "Updated",
        }
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, 200)

        transaction.refresh_from_db()
        self.assertEqual(transaction.date, tomorrow)

        balance_today.refresh_from_db()
        self.assertEqual(balance_today.amount, Decimal(0))  # prev=0, no transactions on today

        balance_tomorrow = BalanceRecord.objects.filter(account=self.account, date=tomorrow).first()
        self.assertIsNotNone(balance_tomorrow)
        self.assertEqual(balance_tomorrow.amount, Decimal(100))  # prev=today=0, income=100

    def test_update__date_changed__to_past(self):
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        balance_today = BalanceRecordFactory.create(account=self.account, date=today, amount="100")

        url = reverse("transactions-detail", args=(transaction.id,))
        data = {
            "account_id": self.account.id,
            "type": TransactionType.INCOME,
            "amount": "100",
            "date": yesterday.isoformat(),
            "description": "Updated",
            "raw_category": "Updated",
        }
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, 200)

        transaction.refresh_from_db()
        self.assertEqual(transaction.date, yesterday)

        balance_yesterday = BalanceRecord.objects.filter(account=self.account, date=yesterday).first()
        self.assertIsNotNone(balance_yesterday)
        self.assertEqual(balance_yesterday.amount, Decimal(100))  # prev=0, income=100

        balance_today.refresh_from_db()
        self.assertEqual(balance_today.amount, Decimal(100))  # prev=yesterday=100, no transactions

    def test_update__date_changed__subsequent_balances_updated(self):
        today = timezone.localdate()
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        balance_today = BalanceRecordFactory.create(account=self.account, date=today, amount="100")
        TransactionFactory.create(
            account=self.account, date=today + timedelta(days=1), amount=Decimal(50), type=TransactionType.INCOME
        )
        balance_tomorrow = BalanceRecordFactory.create(
            account=self.account, date=today + timedelta(days=1), amount=Decimal(150)
        )

        # Move transaction from today to today+2
        url = reverse("transactions-detail", args=(transaction.id,))
        data = {
            "account_id": self.account.id,
            "type": TransactionType.INCOME,
            "amount": "100",
            "date": (today + timedelta(days=2)).isoformat(),
            "description": "Updated",
            "raw_category": "Updated",
        }
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, 200)

        balance_today.refresh_from_db()
        balance_tomorrow.refresh_from_db()
        balance_day_after = BalanceRecord.objects.filter(account=self.account, date=today + timedelta(days=2)).first()

        self.assertEqual(balance_today.amount, Decimal(0))  # no transactions
        self.assertEqual(balance_tomorrow.amount, Decimal(50))  # prev=today=0, income=50
        self.assertIsNotNone(balance_day_after)
        self.assertEqual(balance_day_after.amount, Decimal(150))  # prev=tomorrow=50, income=100

    def test_destroy__transaction_deleted(self):
        today = timezone.localdate()
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        balance_record = BalanceRecordFactory.create(account=self.account, date=today, amount="100")

        url = reverse("transactions-detail", args=(transaction.id,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())

        balance_record.refresh_from_db()
        self.assertEqual(balance_record.amount, Decimal(0))  # prev=0, no transactions left

    def test_destroy__other_transactions_exist_on_date(self):
        today = timezone.localdate()
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        TransactionFactory.create(account=self.account, date=today, amount=Decimal(50), type=TransactionType.INCOME)
        balance_record = BalanceRecordFactory.create(account=self.account, date=today, amount=Decimal(150))

        url = reverse("transactions-detail", args=(transaction.id,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)

        balance_record.refresh_from_db()
        self.assertEqual(balance_record.amount, Decimal(50))  # prev=0, income=50 remaining

    def test_destroy__subsequent_balances_updated(self):
        today = timezone.localdate()
        transaction = TransactionFactory.create(
            account=self.account, amount="100", type=TransactionType.INCOME, date=today
        )
        balance_today = BalanceRecordFactory.create(account=self.account, date=today, amount="100")
        TransactionFactory.create(
            account=self.account, date=today + timedelta(days=1), amount=Decimal(50), type=TransactionType.INCOME
        )
        balance_tomorrow = BalanceRecordFactory.create(
            account=self.account, date=today + timedelta(days=1), amount=Decimal(150)
        )
        TransactionFactory.create(
            account=self.account, date=today + timedelta(days=2), amount=Decimal(20), type=TransactionType.EXPENSE
        )
        balance_day_after = BalanceRecordFactory.create(
            account=self.account, date=today + timedelta(days=2), amount=Decimal(130)
        )

        url = reverse("transactions-detail", args=(transaction.id,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)

        balance_today.refresh_from_db()
        balance_tomorrow.refresh_from_db()
        balance_day_after.refresh_from_db()
        self.assertEqual(balance_today.amount, Decimal(0))  # prev=0, no transactions
        self.assertEqual(balance_tomorrow.amount, Decimal(50))  # 150 - 100
        self.assertEqual(balance_day_after.amount, Decimal(30))  # 130 - 100

    def test_destroy__another_users_transaction(self):
        transaction = TransactionFactory.create(account=self.other_user_account)
        url = reverse("transactions-detail", args=(transaction.id,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Transaction.objects.filter(id=transaction.id).exists())

    def _assert_transaction_fields(self, transaction: Transaction, data: dict):
        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.type, data["type"])
        self.assertEqual(transaction.amount, data["amount"])
        self.assertEqual(transaction.date.isoformat(), data["date"])
        self.assertEqual(transaction.description, data["description"])
        self.assertEqual(transaction.raw_category, data["raw_category"])

    def _assert_balance_records_amounts(self, transaction: Transaction, balance_records_before: dict):
        for balance_record in transaction.account.balance_records.all():
            balance_record_amount_before = balance_records_before.get(balance_record.id)

            if balance_record.date >= transaction.date:
                if balance_record.date == transaction.date and balance_record_amount_before is None:
                    previous_balance_record = (
                        BalanceRecord.objects.filter(account=transaction.account, date__lt=transaction.date)
                        .order_by("-date")
                        .first()
                    )
                    if not previous_balance_record:
                        expected_amount = (
                            transaction.amount if transaction.type == TransactionType.INCOME else -transaction.amount
                        )
                    else:
                        expected_amount = (
                            previous_balance_record.amount + transaction.amount
                            if transaction.type == TransactionType.INCOME
                            else previous_balance_record.amount - transaction.amount
                        )
                    self.assertEqual(balance_record.amount, expected_amount)
                elif transaction.type == TransactionType.EXPENSE:
                    expected_amount = balance_record_amount_before - transaction.amount
                else:
                    expected_amount = balance_record_amount_before + transaction.amount
            else:
                expected_amount = balance_record_amount_before
            self.assertEqual(balance_record.amount, expected_amount)
