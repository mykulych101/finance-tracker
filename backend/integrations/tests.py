from unittest.mock import patch

import requests
from django.test import TestCase

from integrations.models import ExchangeRate
from integrations.monobank import service
from integrations.tasks import refresh_exchange_rates

RATES_FROM_API = [
    {
        "currencyCodeA": 840,
        "currencyCodeB": 980,
        "date": 1552392228,
        "rateBuy": 44.04,
        "rateSell": 44.4346,
        "rateCross": None,
    },
    {
        "currencyCodeA": 978,
        "currencyCodeB": 980,
        "date": 1552392228,
        "rateBuy": 51.25,
        "rateSell": 51.8001,
        "rateCross": None,
    },
]


class GetExchangeRatesTests(TestCase):
    def test_returns_from_cache(self):
        cached = [{"currencyCodeA": 840, "currencyCodeB": 980, "rateBuy": 44.0}]
        with patch("integrations.monobank.service.cache") as mock_cache:
            mock_cache.get.return_value = cached
            with self.assertNumQueries(0):
                result = service.get_exchange_rates()
        self.assertEqual(result, cached)

    def test_falls_back_to_db_and_warms_cache(self):
        ExchangeRate.objects.create(
            currency_code_a=840,
            currency_code_b=980,
            monobank_date=1552392228,
            rate_buy="44.04",
            rate_sell="44.4346",
        )
        with patch("integrations.monobank.service.cache") as mock_cache:
            mock_cache.get.return_value = None
            with self.assertNumQueries(1):
                result = service.get_exchange_rates()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["currencyCodeA"], 840)
        self.assertEqual(result[0]["rateBuy"], 44.04)
        mock_cache.set.assert_called_once_with(service.CACHE_KEY, result, timeout=service.CACHE_TTL)

    def test_returns_empty_on_cold_start(self):
        with patch("integrations.monobank.service.cache") as mock_cache:
            mock_cache.get.return_value = None
            with self.assertNumQueries(1):
                result = service.get_exchange_rates()
        self.assertEqual(result, [])
        mock_cache.set.assert_not_called()


class PersistRatesTests(TestCase):
    def test_writes_to_db_and_warms_cache(self):
        with patch("integrations.monobank.service.cache") as mock_cache:
            service.persist_rates(RATES_FROM_API)
        self.assertEqual(ExchangeRate.objects.count(), 2)
        usd = ExchangeRate.objects.get(currency_code_a=840)
        self.assertEqual(float(usd.rate_buy), 44.04)
        mock_cache.set.assert_called_once_with(service.CACHE_KEY, RATES_FROM_API, timeout=service.CACHE_TTL)

    def test_upsert_existing_row(self):
        ExchangeRate.objects.create(
            currency_code_a=840,
            currency_code_b=980,
            monobank_date=1000000,
            rate_buy="1.0",
            rate_sell="1.0",
        )
        with patch("integrations.monobank.service.cache"):
            service.persist_rates(RATES_FROM_API)
        self.assertEqual(ExchangeRate.objects.count(), 2)
        usd = ExchangeRate.objects.get(currency_code_a=840)
        self.assertEqual(float(usd.rate_buy), 44.04)


class RefreshExchangeRatesTaskTests(TestCase):
    def test_success_fetches_and_persists(self):
        with (
            patch("integrations.tasks.client.fetch_rates", return_value=RATES_FROM_API) as mock_fetch,
            patch("integrations.tasks.service.persist_rates") as mock_persist,
        ):
            refresh_exchange_rates()
        mock_fetch.assert_called_once()
        mock_persist.assert_called_once_with(RATES_FROM_API)

    def test_swallows_network_error(self):
        with (
            patch("integrations.tasks.client.fetch_rates", side_effect=requests.Timeout) as mock_fetch,
            patch("integrations.tasks.service.persist_rates") as mock_persist,
            self.assertLogs("integrations.tasks", level="WARNING"),
        ):
            refresh_exchange_rates()
        mock_fetch.assert_called_once()
        mock_persist.assert_not_called()
