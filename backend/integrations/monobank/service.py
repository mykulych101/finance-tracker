import logging

from django.core.cache import cache

from integrations.models import ExchangeRate

logger = logging.getLogger(__name__)

CACHE_KEY = "monobank:exchange_rates"
CACHE_TTL = 60 * 60  # 1 h — DB is the persistence layer


def get_exchange_rates() -> list[dict]:
    rates = cache.get(CACHE_KEY)
    if rates is not None:
        return rates
    rates = _rates_from_db()
    if rates:
        cache.set(CACHE_KEY, rates, timeout=CACHE_TTL)
        return rates
    logger.warning("No exchange rates available — cache and DB are both empty")
    return []


def persist_rates(rates: list[dict]) -> None:
    for r in rates:
        ExchangeRate.objects.update_or_create(
            currency_code_a=r["currencyCodeA"],
            currency_code_b=r["currencyCodeB"],
            defaults={
                "monobank_date": r["date"],
                "rate_buy": r.get("rateBuy"),
                "rate_sell": r.get("rateSell"),
                "rate_cross": r.get("rateCross"),
            },
        )
    cache.set(CACHE_KEY, rates, timeout=CACHE_TTL)


def _rates_from_db() -> list[dict]:
    return [
        {
            "currencyCodeA": r.currency_code_a,
            "currencyCodeB": r.currency_code_b,
            "date": r.monobank_date,
            "rateBuy": float(r.rate_buy) if r.rate_buy is not None else None,
            "rateSell": float(r.rate_sell) if r.rate_sell is not None else None,
            "rateCross": float(r.rate_cross) if r.rate_cross is not None else None,
        }
        for r in ExchangeRate.objects.all()
    ]
