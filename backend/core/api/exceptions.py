from rest_framework import status
from rest_framework.exceptions import APIException


class ExchangeRateUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Exchange rates are currently unavailable. Please try again later."
    default_code = "exchange_rate_unavailable"
