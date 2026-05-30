import logging

from celery import shared_task

from integrations.monobank import service

logger = logging.getLogger(__name__)


@shared_task
def refresh_exchange_rates():
    service.get_exchange_rates(force_refresh=True)
    logger.info("Exchange rates refreshed")
