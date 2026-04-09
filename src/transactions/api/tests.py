from datetime import timedelta

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
