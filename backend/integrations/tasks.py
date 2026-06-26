import logging

import requests
from celery import shared_task

from integrations.monobank import client, service

logger = logging.getLogger(__name__)


@shared_task
def refresh_exchange_rates():
    try:
        rates = client.fetch_rates()
    except requests.RequestException:
        logger.warning("Failed to fetch exchange rates from Monobank", exc_info=True)
        return
    service.persist_rates(rates)
    logger.info("Exchange rates refreshed (%d entries)", len(rates))
