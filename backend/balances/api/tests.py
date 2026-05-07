from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from accounts.api.factories import AccountFactory
from balances.api.factories import BalanceRecordFactory
from balances.models import BalanceRecord
from core.api.tests import BaseAPITest
from transactions.constants import TransactionType
from transactions.models import Transaction


class BalanceRecordTests(BaseAPITest):
    def setUp(self):
        self.user = self.create_and_login()
        self.list_url = reverse("balances-list")
        self.account = AccountFactory.create(user=self.user)
        self.default_data = {"account": self.account.id, "amount": 100.0, "date": "2024-01-01", "note": "Test record"}
        self.other_user = self.create(email="test3@mail.com", password="qwerty123456", name="John Snow 3")
        self.other_user_account = AccountFactory.create(user=self.other_user)

    def test_retrieve_balance_records(self):
        balances_count = 5
        BalanceRecordFactory.create_batch(balances_count, account=self.account)
        BalanceRecordFactory.create_batch(balances_count, account=self.other_user_account)
        self.assertEqual(BalanceRecord.objects.count(), balances_count * 2)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], balances_count)
        required_fields = {"id", "account", "amount", "date", "note", "created_at"}
        for field in required_fields:
            self.assertIn(field, resp.data["results"][0])

    def test_retrieve_balance_record_by_id(self):
        balance = BalanceRecordFactory.create(account=self.account)
        url = reverse("balances-detail", args=(balance.id,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], balance.id)
        self.assertEqual(resp.data["account"], balance.account.id)
        self.assertEqual(Decimal(resp.data["amount"]), balance.amount)
        self.assertEqual(resp.data["date"], balance.date.isoformat())
        self.assertEqual(resp.data["note"], balance.note)

    def test_retrieve_latest_balance_records_per_account(self):
        accounts_count = 3
        url = reverse("balances-latest")
        accounts = AccountFactory.create_batch(accounts_count, user=self.user)
        AccountFactory.create(user=self.other_user)
        for account in accounts:
            BalanceRecordFactory.create(account=account, amount=100.0, date="2024-01-01")
            BalanceRecordFactory.create(account=account, amount=200.0, date="2024-02-01")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), accounts_count)
        for record in resp.data:
            self.assertIn("account_id", record)
            self.assertIn("account_name", record)
            self.assertIn("amount", record)
            self.assertIn("date", record)
            self.assertEqual(record["amount"], "200.00")
            self.assertEqual(record["date"], "2024-02-01")

    def test_create_balance_record_missing_fields(self):
        resp = self.client.post(self.list_url, {"amount": 100.0})
        self.assertEqual(resp.status_code, 400)

    def test_create_balance_record_with_invalid_account(self):
        data = self.default_data.copy()
        data["account"] = self.other_user_account.id
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("You can only add balance records to your own accounts", resp.data["account"][0])

    def test_create_balance_record_valid_payload(self):
        balance_records_count = 5
        # Prepare balance records before including the one on the transaction date
        for i in range(1, balance_records_count + 1):
            BalanceRecordFactory.create(account=self.account, date=timezone.localdate() - timedelta(days=i), amount=100)
        # Prepare balance records after
        for i in range(balance_records_count):
            BalanceRecordFactory.create(
                account=self.account, date=timezone.localdate() + timedelta(days=i + 1), amount=100
            )
        balance_records_before = {br.id: br.amount for br in BalanceRecord.objects.all()}
        data = self.default_data.copy()
        data["date"] = timezone.localdate().isoformat()
        data["amount"] = 200
        prev_day_amount = Decimal(100)
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        balance = BalanceRecord.objects.get(account=self.account, date=data["date"])
        self.assertEqual(balance.amount, data["amount"])
        self.assertEqual(balance.date, date.fromisoformat(data["date"]))
        self.assertEqual(balance.note, self.default_data["note"])
        transaction = Transaction.objects.filter(account=self.account, date=data["date"], is_system=True).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, Decimal(str(data["amount"])) - prev_day_amount)
        self.assertEqual(transaction.type, TransactionType.INCOME)
        specified_amount = Decimal(str(data["amount"]))
        propagation_delta = specified_amount - prev_day_amount
        self._assert_balance_records_amounts(balance, specified_amount, propagation_delta, balance_records_before)

    def test_create_balance_record_delta_uses_prev_day_balance(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        yesterday_amount = 100
        today = timezone.localdate().isoformat()
        today_amount = 500
        BalanceRecordFactory.create(account=self.account, amount=yesterday_amount, date=yesterday)

        resp = self.client.post(self.list_url, {**self.default_data, "date": today, "amount": today_amount})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.filter(account=self.account, date=today, is_system=True).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, today_amount - yesterday_amount)
        self.assertEqual(transaction.type, TransactionType.INCOME)

    def test_non_system_transaction_updates_balance_record(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        today = timezone.localdate().isoformat()
        BalanceRecordFactory.create(account=self.account, amount=100, date=yesterday)
        self.client.post(self.list_url, {**self.default_data, "date": today, "amount": 500})

        resp = self.client.post(
            reverse("transactions-list"),
            {
                "account_id": self.account.id,
                "type": TransactionType.INCOME,
                "amount": 30,
                "date": today,
                "description": "Test transaction",
                "raw_category": "Salary",
            },
        )
        self.assertEqual(resp.status_code, 201)
        balance_record_today = BalanceRecord.objects.get(account=self.account, date=today)
        self.assertEqual(balance_record_today.amount, 530)

    def test_update_balance_record_uses_incremental_delta(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        today = timezone.localdate().isoformat()
        initial_amount = 500
        non_system_amount = 30
        updated_amount = 600
        BalanceRecordFactory.create(account=self.account, amount=100, date=yesterday)
        self.client.post(self.list_url, {**self.default_data, "date": today, "amount": initial_amount})
        self.client.post(
            reverse("transactions-list"),
            {
                "account_id": self.account.id,
                "type": TransactionType.INCOME,
                "amount": non_system_amount,
                "date": today,
                "description": "Test transaction",
                "raw_category": "Salary",
            },
        )
        balance_after_non_system = initial_amount + non_system_amount  # 530

        resp = self.client.post(
            self.list_url, {"date": today, "account": self.account.id, "amount": updated_amount, "note": "Updated"}
        )
        self.assertEqual(resp.status_code, 201)
        balance_record_today = BalanceRecord.objects.get(account=self.account, date=today)
        self.assertEqual(balance_record_today.amount, updated_amount)
        self.assertEqual(Transaction.objects.count(), 3)
        expected_delta = updated_amount - balance_after_non_system  # 70
        transaction = Transaction.objects.filter(
            account=self.account, date=today, is_system=True, amount=expected_delta
        ).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.type, TransactionType.INCOME)

    def test_update_balance_record_propagates_to_subsequent(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        yesterday_amount = 100
        today = timezone.localdate().isoformat()
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        tomorrow_amount = 800
        updated_amount = 600
        BalanceRecordFactory.create(account=self.account, amount=yesterday_amount, date=yesterday)
        BalanceRecordFactory.create(account=self.account, amount=tomorrow_amount, date=tomorrow)
        self.client.post(self.list_url, {**self.default_data, "date": today, "amount": 500})
        self.client.post(
            reverse("transactions-list"),
            {
                "account_id": self.account.id,
                "type": TransactionType.INCOME,
                "amount": 30,
                "date": today,
                "description": "Test transaction",
                "raw_category": "Salary",
            },
        )
        self.client.post(
            self.list_url, {"date": today, "account": self.account.id, "amount": updated_amount, "note": "Updated"}
        )

        balance_record_tomorrow = BalanceRecord.objects.get(account=self.account, date=tomorrow)
        self.assertEqual(balance_record_tomorrow.amount, tomorrow_amount + (updated_amount - yesterday_amount))

    def test_create_balance_record_duplicate_date(self):
        date = "2024-01-01"
        resp = self.client.post(self.list_url, self.default_data)
        self.assertEqual(resp.status_code, 201)
        balance = BalanceRecord.objects.get(account=self.account, date=date)
        balance.amount = self.default_data["amount"]
        balance.note = self.default_data["note"]
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.filter(account=self.account, date=date, is_system=True).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, self.default_data["amount"])
        self.assertEqual(transaction.type, TransactionType.INCOME)

        data = self.default_data.copy()
        data["date"] = date
        data["amount"] = 10.0
        data["note"] = "Second record"
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        balance.refresh_from_db()
        self.assertEqual(balance.amount, data["amount"])
        self.assertEqual(balance.note, data["note"])
        self.assertEqual(Transaction.objects.count(), 2)
        expected_delta = abs(Decimal(str(data["amount"])) - Decimal(str(self.default_data["amount"])))
        transaction = Transaction.objects.filter(
            account=self.account, amount=expected_delta, date=date, is_system=True
        ).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, expected_delta)
        self.assertEqual(transaction.type, TransactionType.EXPENSE)

    def test_create_balance_record_with_future_date(self):
        future_date = (timezone.localdate() + timedelta(days=1)).isoformat()
        data = self.default_data.copy()
        data["date"] = future_date
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("The date cannot be in the future", resp.data["date"][0])

    def test_delete_balance_record(self):
        balance = BalanceRecordFactory.create(account=self.account)
        url = reverse("balances-detail", args=(balance.id,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(BalanceRecord.objects.filter(id=balance.id).exists())

    def test_delete_nonexistent_balance_record(self):
        url = reverse("balances-detail", args=(999,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)

    def test_create_balance_record_negative_delta(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        BalanceRecordFactory.create(account=self.account, amount=500, date=yesterday)

        data = self.default_data.copy()
        data["date"] = timezone.localdate().isoformat()
        data["amount"] = 200
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)

        transaction = Transaction.objects.filter(account=self.account, is_system=True).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.amount, Decimal(300))
        self.assertEqual(transaction.type, TransactionType.EXPENSE)

    def test_retrieve_other_user_balance_record(self):
        balance = BalanceRecordFactory.create(account=self.other_user_account)
        url = reverse("balances-detail", args=(balance.id,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_delete_other_user_balance_record(self):
        balance = BalanceRecordFactory.create(account=self.other_user_account)
        url = reverse("balances-detail", args=(balance.id,))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)

    def test_unauthenticated_access(self):
        self.client.logout()
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 401)

    def test_no_recursion_balance_record_create_does_not_trigger_recalculate(self):
        with patch("transactions.api.services.recalculate_balance_on_date") as mock:
            resp = self.client.post(self.list_url, self.default_data)
            self.assertEqual(resp.status_code, 201)
            mock.assert_not_called()

    def _assert_balance_records_amounts(
        self,
        balance_record: BalanceRecord,
        specified_amount: Decimal,
        propagation_delta: Decimal,
        balance_records_before: dict,
    ):
        for br in balance_record.account.balance_records.all():
            amount_before = balance_records_before.get(br.id)
            if br.date == balance_record.date:
                self.assertEqual(br.amount, specified_amount)
            elif br.date > balance_record.date:
                self.assertEqual(br.amount, amount_before + propagation_delta)
            else:
                self.assertEqual(br.amount, amount_before)
