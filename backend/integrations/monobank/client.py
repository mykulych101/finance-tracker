import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_rates() -> list[dict]:
    url = settings.MONOBANK_API_URL.rstrip("/") + "/bank/currency"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
