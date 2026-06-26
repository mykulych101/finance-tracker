from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from accounts.api.factories import AccountFactory
from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account
from balances.api.factories import BalanceRecordFactory
from core.api.tests import MOCK_RATES, BaseAPITest


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
            currency=AccountCurrency.UAH,
        )
        AccountFactory.create_batch(
            2,
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.MORTGAGE,
            currency=AccountCurrency.UAH,
        )
        credit_card_account = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.CREDIT_CARD,
            currency=AccountCurrency.UAH,
            credit_limit=10000,
        )

        self.assertEqual(Account.objects.count(), 5)

        for i, account in enumerate(Account.objects.filter(type=AccountType.ASSET)):
            BalanceRecordFactory.create(account=account, amount=10000, date=date_now if i % 2 == 0 else date_past)

        for i, account in enumerate(Account.objects.filter(type=AccountType.LIABILITY)):
            BalanceRecordFactory.create(account=account, amount=4000, date=date_now if i % 2 == 0 else date_past)

        BalanceRecordFactory.create(account=credit_card_account, amount=2000, date=date_now)
        BalanceRecordFactory.create(account=credit_card_account, amount=3000, date=date_past)

        url = reverse("analytics-net-worth")
        with patch("analytics.api.views.get_exchange_rates", return_value=[]), self.assertNumQueries(2):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["assets_total"], 20000)
        self.assertEqual(response.data["liabilities_total"], 16000)
        self.assertEqual(response.data["net_worth"], 4000)
        self.assertEqual(len(response.data["accounts"]), 5)

        # Test with date filter
        response = self.client.get(url + f"?date={date_past}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["assets_total"], 10000)
        self.assertEqual(response.data["liabilities_total"], 11000)
        self.assertEqual(response.data["net_worth"], -1000)
        self.assertEqual(len(response.data["accounts"]), 5)

    def test_net_worth_convert_to_usd(self):
        today = timezone.localdate()
        asset = AccountFactory.create(
            user=self.user, type=AccountType.ASSET, category=AccountCategory.CASH, currency=AccountCurrency.UAH
        )
        liability = AccountFactory.create(
            user=self.user, type=AccountType.LIABILITY, category=AccountCategory.MORTGAGE, currency=AccountCurrency.UAH
        )
        BalanceRecordFactory.create(account=asset, amount=10000, date=today)
        BalanceRecordFactory.create(account=liability, amount=4000, date=today)

        url = reverse("analytics-net-worth") + "?convert_to=USD"
        with patch("analytics.api.views.get_exchange_rates", return_value=MOCK_RATES):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data["assets_total"]), Decimal("225.05"))
        self.assertEqual(Decimal(response.data["liabilities_total"]), Decimal("90.02"))
        self.assertEqual(Decimal(response.data["net_worth"]), Decimal("135.03"))

    def test_net_worth_convert_to_usd_credit_card(self):
        today = timezone.localdate()
        credit_card = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.CREDIT_CARD,
            currency=AccountCurrency.UAH,
            credit_limit=10000,
        )
        BalanceRecordFactory.create(account=credit_card, amount=2000, date=today)

        url = reverse("analytics-net-worth") + "?convert_to=USD"
        with patch("analytics.api.views.get_exchange_rates", return_value=MOCK_RATES):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data["assets_total"]), Decimal("0.00"))
        self.assertEqual(Decimal(response.data["liabilities_total"]), Decimal("180.04"))
        self.assertEqual(Decimal(response.data["net_worth"]), Decimal("-180.04"))

    def test_net_worth_default_converts_to_uan(self):
        today = timezone.localdate()
        usd_asset = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.USD,
        )
        uan_asset = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=usd_asset, amount=100, date=today)
        BalanceRecordFactory.create(account=uan_asset, amount=10000, date=today)

        url = reverse("analytics-net-worth")
        with patch("analytics.api.views.get_exchange_rates", return_value=MOCK_RATES):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data["assets_total"]), Decimal("14404.00"))
        self.assertEqual(Decimal(response.data["liabilities_total"]), Decimal("0.00"))
        self.assertEqual(Decimal(response.data["net_worth"]), Decimal("14404.00"))
