from django_filters import FilterSet, filters

from balances.models import BalanceRecord


class BalanceRecordFilters(FilterSet):
    date = filters.DateFilter(field_name="date", lookup_expr="exact")

    class Meta:
        model = BalanceRecord
        fields = ("date",)
