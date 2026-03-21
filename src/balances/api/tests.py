from datetime import date, timedelta

from django.urls import reverse
from django.utils import timezone

from accounts.api.factories import AccountFactory
from balances.models import BalanceRecord
from core.api.tests import BaseAPITest


class BalanceRecordTests(BaseAPITest):
    def setUp(self):
        self.user = self.create_and_login()
        self.list_url = reverse("balances-list")
        self.account = AccountFactory.create(user=self.user)
        self.default_data = {"account": self.account.id, "amount": 100.0, "date": "2024-01-01", "note": "Test record"}

    def test_create_balance_record_missing_fields(self):
        resp = self.client.post(self.list_url, {"amount": 100.0})
        self.assertEqual(resp.status_code, 400)

    def test_create_balance_record_with_invalid_account(self):
        another_user = self.create(email="test3@mail.com", password="qwerty123456", name="John Snow 3")
        another_account = AccountFactory.create(user=another_user)
        data = self.default_data.copy()
        data["account"] = another_account.id
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
