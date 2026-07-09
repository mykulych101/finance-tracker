from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django_filters import FilterSet, filters

from balances.models import BalanceRecord

_PERIOD_TRUNC = {
    "daily": TruncDay,
    "weekly": TruncWeek,
    "monthly": TruncMonth,
}


class AnalyticsNetWorthHistoryFilter(FilterSet):
    date = filters.DateFromToRangeFilter(field_name="date")
    period = filters.ChoiceFilter(
        choices=[("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
        method="filter_period",
    )

    class Meta:
        model = BalanceRecord
        fields = ("id", "account", "date", "period")

    def filter_period(self, queryset, name, value):
        trunc_func = _PERIOD_TRUNC.get(value)
        if trunc_func:
            return queryset.annotate(period_date=trunc_func("date"))
        return queryset
