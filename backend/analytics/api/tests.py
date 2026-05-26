from django.urls import reverse
from django.utils import timezone

from accounts.api.factories import AccountFactory
from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account
from balances.api.factories import BalanceRecordFactory
from core.api.tests import BaseAPITest


class AnalyticsTests(BaseAPITest):
    def setUp(self):
        self.user = self.create_and_login()

    def test_net_worth(self):
        date_now = timezone.localdate()
        date_past = date_now - timezone.timedelta(days=30)
        AccountFactory.create_batch(
            2,
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            is_active=True,
            currency=AccountCurrency.USD,
        )
        AccountFactory.create_batch(
            2,
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.MORTGAGE,
            is_active=True,
            currency=AccountCurrency.USD,
        )

        self.assertEqual(Account.objects.count(), 4)

        for i, account in enumerate(Account.objects.filter(type=AccountType.ASSET)):
            BalanceRecordFactory(account=account, amount=100, date=date_now if i % 2 == 0 else date_past)

        for i, account in enumerate(Account.objects.filter(type=AccountType.LIABILITY)):
            BalanceRecordFactory(account=account, amount=40, date=date_now if i % 2 == 0 else date_past)

        url = reverse("analytics-net-worth")
        with self.assertNumQueries(4):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["date"], str(date_now))
        self.assertEqual(response.data["assets_total"], 200)
        self.assertEqual(response.data["liabilities_total"], 80)
        self.assertEqual(response.data["net_worth"], 120)
        self.assertEqual(len(response.data["accounts"]), 4)

        # Test with date filter
        response = self.client.get(url + f"?date={date_past}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["date"], str(date_now))
        self.assertEqual(response.data["assets_total"], 100)
        self.assertEqual(response.data["liabilities_total"], 40)
        self.assertEqual(response.data["net_worth"], 60)
        self.assertEqual(len(response.data["accounts"]), 4)
