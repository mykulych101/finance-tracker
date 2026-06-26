from decimal import ROUND_HALF_UP, Decimal

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account
from analytics.api.serializers import AnalyticsNetWorthSerializer
from integrations.monobank.converter import convert_amount
from integrations.monobank.service import get_exchange_rates


@extend_schema_view(
    net_worth=extend_schema(
        parameters=[
            OpenApiParameter(
                name="convert_to",
                location=OpenApiParameter.QUERY,
                required=False,
                enum=AccountCurrency.values,
                description="Convert all balances to this currency.",
            )
        ]
    )
)
class AnalyticsViewSet(GenericViewSet):
    def get_queryset(self, **kwargs):
        return Account.objects.with_latest_balance(**kwargs).filter(user=self.request.user, is_active=True)

    @extend_schema(
        request=None,
        responses={200: AnalyticsNetWorthSerializer},
        description="Get net worth summary for the user.",
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="As-of date (YYYY-MM-DD). Defaults to today.",
            )
        ],
    )
    @action(detail=False, methods=["GET"])
    def net_worth(self, request, *args, **kwargs):
        balance_date = request.query_params.get("date")
        convert_to = request.query_params.get("convert_to", AccountCurrency.UAH)
        if convert_to not in AccountCurrency.values:
            convert_to = None

        accounts = self.get_queryset(balance_date=balance_date)

        accounts = list(accounts)
        rates = get_exchange_rates() if convert_to else []
        assets_total = Decimal(0)
        liabilities_total = Decimal(0)
        for account in accounts:
            balance = Decimal(str(account.latest_balance or 0))
            if convert_to:
                balance = convert_amount(balance, account.currency, convert_to, rates)

            if account.type == AccountType.ASSET:
                assets_total += balance
            elif account.type == AccountType.LIABILITY:
                if account.category == AccountCategory.CREDIT_CARD:
                    limit = Decimal(str(account.credit_limit or 0))
                    if convert_to:
                        limit = convert_amount(limit, account.currency, convert_to, rates)
                    liabilities_total += limit - balance
                else:
                    liabilities_total += balance

        assets_total = assets_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        liabilities_total = liabilities_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        serializer = AnalyticsNetWorthSerializer(
            {
                "accounts": accounts,
                "assets_total": assets_total,
                "liabilities_total": liabilities_total,
                "net_worth": assets_total - liabilities_total,
            },
            context={"convert_to": convert_to, "rates": rates} if convert_to else {},
        )

        return Response(serializer.data)
