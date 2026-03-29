from datetime import date, timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from accounts.api.factories import AccountFactory
from balances.api.factories import BalanceRecordFactory
from balances.models import BalanceRecord
from core.api.tests import BaseAPITest


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
        resp = self.client.post(self.list_url, self.default_data)
        self.assertEqual(resp.status_code, 201)
        balance = BalanceRecord.objects.get(account=self.account)
        self.assertEqual(balance.amount, self.default_data["amount"])
        self.assertEqual(balance.date, date.fromisoformat(self.default_data["date"]))
        self.assertEqual(balance.note, self.default_data["note"])

    def test_create_balance_record_duplicate_date(self):
        date = "2024-01-01"
        balance = BalanceRecord.objects.create(account=self.account, amount=100.0, date=date, note="First record")
        data = self.default_data.copy()
        data["date"] = date
        data["amount"] = 200.0
        data["note"] = "Second record"
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, 201)
        balance.refresh_from_db()
        self.assertEqual(balance.amount, data["amount"])
        self.assertEqual(balance.note, data["note"])

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
