import logging

from django.core.cache import cache

from . import client

logger = logging.getLogger(__name__)

CACHE_KEY = "monobank:exchange_rates"
CACHE_TTL = 60 * 60 * 24  # 24 hours


def get_exchange_rates(*, force_refresh: bool = False) -> list[dict]:
    rates = cache.get(CACHE_KEY)
    if rates is None or force_refresh:
        logger.info("Fetching exchange rates from Monobank")
        rates = client.fetch_rates()
        cache.set(CACHE_KEY, rates, timeout=CACHE_TTL)
    return rates
