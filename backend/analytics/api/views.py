from collections import defaultdict

from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from accounts.constants import AccountCurrency
from accounts.models import Account
from analytics.api.filters import AnalyticsNetWorthHistoryFilter
from analytics.api.serializers import AnalyticsNetWorthHistoryItemSerializer, AnalyticsNetWorthSerializer
from analytics.utils import aggregate_net_worth, aggregate_net_worth_history, generate_buckets
from balances.models import BalanceRecord
from core.api.exceptions import ExchangeRateUnavailable
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
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "net_worth_history":
            return AnalyticsNetWorthHistoryItemSerializer
        return AnalyticsNetWorthSerializer

    @property
    def filterset_class(self):
        if self.action == "net_worth_history":
            return AnalyticsNetWorthHistoryFilter
        return None

    def get_queryset(self, **kwargs):
        # TODO: remove
        if getattr(self, "swagger_fake_view", False):
            return BalanceRecord.objects.none() if self.action == "net_worth_history" else Account.objects.none()
        if self.action == "net_worth_history":
            return BalanceRecord.objects.filter(
                account__user=self.request.user, account__is_active=True
            ).select_related("account")
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
        rates = get_exchange_rates() if convert_to else []

        accounts = self.get_queryset(balance_date=balance_date)

        accounts = list(accounts)
        try:
            assets_total, liabilities_total = aggregate_net_worth(accounts, convert_to, rates)
        except ValueError as exc:
            raise ExchangeRateUnavailable from exc

        serializer = AnalyticsNetWorthSerializer(
            {
                "accounts": accounts,
                "assets_total": assets_total,
                "liabilities_total": liabilities_total,
                "net_worth": assets_total - liabilities_total,
            },
        )

        return Response(serializer.data)

    @extend_schema(
        request=None,
        responses={200: AnalyticsNetWorthHistoryItemSerializer(many=True)},
        description="Get net worth history for the user.",
        parameters=[
            OpenApiParameter(
                name="convert_to",
                location=OpenApiParameter.QUERY,
                required=False,
                enum=AccountCurrency.values,
                description="Convert all balances to this currency.",
            )
        ],
    )
    @action(detail=False, methods=["GET"], url_path="net-worth-history")
    def net_worth_history(self, request, *args, **kwargs):
        filterset = self.filterset_class(data=request.query_params)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        cleaned = filterset.form.cleaned_data
        date_range = cleaned.get("date")
        date_after = date_range.start.date() if date_range and date_range.start else None
        date_before = date_range.stop.date() if date_range and date_range.stop else None
        if not (date_after and date_before):
            return Response([])

        convert_to = request.query_params.get("convert_to", AccountCurrency.UAH)
        if convert_to not in AccountCurrency.values:
            convert_to = None
        rates = get_exchange_rates() if convert_to else []

        # Single fetch: every record up to date_before (no lower bound so balances carry forward).
        records = self.get_queryset().filter(date__lte=date_before).order_by("date", "created_at")
        if cleaned.get("account"):
            records = records.filter(account=cleaned["account"])

        accounts = {}
        records_by_account = defaultdict(list)
        for record in records:
            accounts.setdefault(record.account_id, record.account)
            records_by_account[record.account_id].append((record.date, record.amount))

        buckets = generate_buckets(date_after, date_before, cleaned.get("period"))
        try:
            history = aggregate_net_worth_history(
                list(accounts.values()), records_by_account, buckets, convert_to, rates
            )
        except ValueError as exc:
            raise ExchangeRateUnavailable from exc

        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
