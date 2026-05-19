from django_filters import FilterSet, filters

from transactions.constants import TransactionType
from transactions.models import Transaction


class TransactionFilters(FilterSet):
    account = filters.BaseInFilter(field_name="account", lookup_expr="in")
    type = filters.ChoiceFilter(field_name="type", lookup_expr="exact", choices=TransactionType.choices)
    amount = filters.RangeFilter(field_name="amount")
    date = filters.DateFromToRangeFilter(field_name="date")
    description = filters.CharFilter(field_name="description", lookup_expr="icontains")
    raw_category = filters.CharFilter(field_name="raw_category", lookup_expr="icontains")
    is_system = filters.BooleanFilter(field_name="is_system")

    class Meta:
        model = Transaction
        fields = ("account", "type", "amount", "date", "description", "raw_category", "is_system")
