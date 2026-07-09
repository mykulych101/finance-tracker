from datetime import date
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

    def test_net_worth_no_rates_returns_503(self):
        today = timezone.localdate()
        asset = AccountFactory.create(
            user=self.user, type=AccountType.ASSET, category=AccountCategory.CASH, currency=AccountCurrency.UAH
        )
        BalanceRecordFactory.create(account=asset, amount=10000, date=today)

        url = reverse("analytics-net-worth") + "?convert_to=USD"
        with patch("analytics.api.views.get_exchange_rates", return_value=[]):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 503)

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

    def test_net_worth_history(self):
        today = timezone.localdate()
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=1000, date=today)
        BalanceRecordFactory.create(account=account, amount=2000, date=today + timezone.timedelta(days=2))
        resp = self.client.get(
            url + f"?date_after={today}&date_before={today + timezone.timedelta(days=3)}&period=daily"
        )
        self.assertEqual(resp.status_code, 200)

    def test_net_worth_history_daily(self):
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=1000, date=date(2025, 1, 1))
        BalanceRecordFactory.create(account=account, amount=2000, date=date(2025, 1, 3))

        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-03&period=daily")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        self.assertEqual(response.data[0]["date"], "2025-01-01")
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("1000.00"))
        self.assertEqual(Decimal(response.data[0]["assets"]), Decimal("1000.00"))
        self.assertEqual(Decimal(response.data[0]["liabilities"]), Decimal("0.00"))

        # Jan 2 has no record — balance carries forward from Jan 1
        self.assertEqual(response.data[1]["date"], "2025-01-02")
        self.assertEqual(Decimal(response.data[1]["net_worth"]), Decimal("1000.00"))

        self.assertEqual(response.data[2]["date"], "2025-01-03")
        self.assertEqual(Decimal(response.data[2]["net_worth"]), Decimal("2000.00"))

    def test_net_worth_history_weekly(self):
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=1000, date=date(2025, 1, 3))
        BalanceRecordFactory.create(account=account, amount=2000, date=date(2025, 1, 10))

        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-19&period=weekly")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # Jan 1 is Wednesday → first bucket is Sunday Jan 5
        self.assertEqual(response.data[0]["date"], "2025-01-05")
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("1000.00"))

        self.assertEqual(response.data[1]["date"], "2025-01-12")
        self.assertEqual(Decimal(response.data[1]["net_worth"]), Decimal("2000.00"))

        # No record in week ending Jan 19 — carries forward from Jan 10
        self.assertEqual(response.data[2]["date"], "2025-01-19")
        self.assertEqual(Decimal(response.data[2]["net_worth"]), Decimal("2000.00"))

    def test_net_worth_history_monthly(self):
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=1000, date=date(2025, 1, 10))
        BalanceRecordFactory.create(account=account, amount=2000, date=date(2025, 2, 10))
        BalanceRecordFactory.create(account=account, amount=3000, date=date(2025, 3, 10))

        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-03-31&period=monthly")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["date"], "2025-01-31")
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("1000.00"))
        self.assertEqual(response.data[1]["date"], "2025-02-28")
        self.assertEqual(Decimal(response.data[1]["net_worth"]), Decimal("2000.00"))
        self.assertEqual(response.data[2]["date"], "2025-03-31")
        self.assertEqual(Decimal(response.data[2]["net_worth"]), Decimal("3000.00"))

    def test_net_worth_history_carry_forward(self):
        """Account with no updates in requested range should use the last balance before date_after."""
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=5000, date=date(2024, 12, 15))

        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-31&period=monthly")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["date"], "2025-01-31")
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("5000.00"))

    def test_net_worth_history_date_before_filter(self):
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=1000, date=date(2025, 1, 10))
        BalanceRecordFactory.create(account=account, amount=9999, date=date(2025, 2, 15))

        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-31&period=monthly")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("1000.00"))

    def test_net_worth_history_user_isolation(self):
        other_user = self.create("other@example.com", "password123", "Other User")
        url = reverse("analytics-net-worth-history")
        my_account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        other_account = AccountFactory.create(
            user=other_user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=my_account, amount=1000, date=date(2025, 1, 10))
        BalanceRecordFactory.create(account=other_account, amount=9999, date=date(2025, 1, 10))

        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-31&period=monthly")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("1000.00"))

    def test_net_worth_history_filter_by_account(self):
        url = reverse("analytics-net-worth-history")
        account1 = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        account2 = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account1, amount=1000, date=date(2025, 1, 10))
        BalanceRecordFactory.create(account=account2, amount=9999, date=date(2025, 1, 10))

        response = self.client.get(
            url + f"?date_after=2025-01-01&date_before=2025-01-31&period=monthly&account={account1.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("1000.00"))

    def test_net_worth_history_unauthenticated(self):
        self.client.credentials()
        url = reverse("analytics-net-worth-history")
        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-31&period=daily")
        self.assertEqual(response.status_code, 401)

    def test_net_worth_history_invalid_period(self):
        url = reverse("analytics-net-worth-history")
        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-31&period=quarterly")
        self.assertEqual(response.status_code, 400)

    def test_net_worth_history_currency_conversion(self):
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=10000, date=date(2025, 1, 10))

        with patch("analytics.api.views.get_exchange_rates", return_value=MOCK_RATES):
            response = self.client.get(
                url + "?date_after=2025-01-01&date_before=2025-01-31&period=monthly&convert_to=USD"
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("225.05"))
        self.assertEqual(Decimal(response.data[0]["assets"]), Decimal("225.05"))

    def test_net_worth_history_no_rates_returns_503(self):
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create(account=account, amount=10000, date=date(2025, 1, 10))

        with patch("analytics.api.views.get_exchange_rates", return_value=[]):
            response = self.client.get(
                reverse("analytics-net-worth-history")
                + "?date_after=2025-01-01&date_before=2025-01-31&period=monthly&convert_to=USD"
            )
        self.assertEqual(response.status_code, 503)

    def test_net_worth_history_query_count(self):
        url = reverse("analytics-net-worth-history")
        account = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        BalanceRecordFactory.create_batch(3, account=account, date=date(2025, 1, 10))

        with patch("analytics.api.views.get_exchange_rates", return_value=[]), self.assertNumQueries(2):
            response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-31&period=monthly")
        self.assertEqual(response.status_code, 200)

    def test_net_worth_history_query_count_constant_across_buckets(self):
        """Query count must not grow with the number of buckets (N+1 regression guard)."""
        url = reverse("analytics-net-worth-history")
        for _ in range(3):
            account = AccountFactory.create(
                user=self.user,
                type=AccountType.ASSET,
                category=AccountCategory.CASH,
                currency=AccountCurrency.UAH,
            )
            BalanceRecordFactory.create_batch(2, account=account, date=date(2025, 1, 5))

        # Daily over a month → 31 buckets; the old per-bucket implementation issued one query each.
        with patch("analytics.api.views.get_exchange_rates", return_value=[]), self.assertNumQueries(2):
            response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-31&period=daily")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 31)

    def test_net_worth_history_multiple_accounts(self):
        """Each bucket sums across accounts, including the credit-card limit-minus-balance path."""
        url = reverse("analytics-net-worth-history")
        asset = AccountFactory.create(
            user=self.user,
            type=AccountType.ASSET,
            category=AccountCategory.CASH,
            currency=AccountCurrency.UAH,
        )
        mortgage = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.MORTGAGE,
            currency=AccountCurrency.UAH,
        )
        credit_card = AccountFactory.create(
            user=self.user,
            type=AccountType.LIABILITY,
            category=AccountCategory.CREDIT_CARD,
            currency=AccountCurrency.UAH,
            credit_limit=10000,
        )
        BalanceRecordFactory.create(account=asset, amount=10000, date=date(2025, 1, 1))
        BalanceRecordFactory.create(account=mortgage, amount=4000, date=date(2025, 1, 1))
        BalanceRecordFactory.create(account=credit_card, amount=2000, date=date(2025, 1, 1))

        response = self.client.get(url + "?date_after=2025-01-01&date_before=2025-01-02&period=daily")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # assets = 10000; liabilities = 4000 (mortgage) + (10000 - 2000) (credit card) = 12000
        self.assertEqual(Decimal(response.data[0]["assets"]), Decimal("10000.00"))
        self.assertEqual(Decimal(response.data[0]["liabilities"]), Decimal("12000.00"))
        self.assertEqual(Decimal(response.data[0]["net_worth"]), Decimal("-2000.00"))

        # Jan 2 has no new records — every account carries forward unchanged.
        self.assertEqual(Decimal(response.data[1]["net_worth"]), Decimal("-2000.00"))
