from django.db.models import Case, DecimalField, ExpressionWrapper, F, Sum, When
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from accounts.constants import AccountCategory, AccountType
from accounts.models import Account
from analytics.api.serializers import AnalyticsNetWorthSerializer


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

        accounts = self.get_queryset(balance_date=balance_date)

        assets_total = accounts.filter(type=AccountType.ASSET).aggregate(total=Sum("latest_balance"))["total"] or 0
        liabilities_total = (
            accounts.filter(type=AccountType.LIABILITY)
            .annotate(
                effective_balance=Case(
                    When(
                        category=AccountCategory.CREDIT_CARD,
                        then=ExpressionWrapper(F("credit_limit") - F("latest_balance"), output_field=DecimalField()),
                    ),
                    default=F("latest_balance"),
                    output_field=DecimalField(),
                )
            )
            .aggregate(total=Sum("effective_balance"))["total"]
            or 0
        )

        serializer = AnalyticsNetWorthSerializer(
            {
                "accounts": accounts,
                "assets_total": assets_total,
                "liabilities_total": liabilities_total,
                "net_worth": assets_total - liabilities_total,
            }
        )

        return Response(serializer.data)
