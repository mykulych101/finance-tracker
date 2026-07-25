from django.db.models import Case, DecimalField, F, When
from django_filters import FilterSet, filters

from transactions.constants import TransactionType
from transactions.models import Transaction


class SignedAmountOrderingFilter(filters.OrderingFilter):
    def filter(self, qs, value):
        if value and any(v in ("amount", "-amount") for v in value):
            qs = qs.annotate(
                signed_amount=Case(
                    When(type=TransactionType.EXPENSE, then=-F("amount")),
                    default=F("amount"),
                    output_field=DecimalField(),
                )
            )
            value = ["signed_amount" if v == "amount" else "-signed_amount" if v == "-amount" else v for v in value]
        return super().filter(qs, value)


class TransactionFilters(FilterSet):
    account = filters.BaseInFilter(field_name="account", lookup_expr="in")
    type = filters.ChoiceFilter(field_name="type", lookup_expr="exact", choices=TransactionType.choices)
    amount = filters.RangeFilter(field_name="amount")
    date = filters.DateFromToRangeFilter(field_name="date")
    description = filters.CharFilter(field_name="description", lookup_expr="icontains")
    raw_category = filters.CharFilter(field_name="raw_category", lookup_expr="icontains")
    is_system = filters.BooleanFilter(field_name="is_system")

    ordering = SignedAmountOrderingFilter(
        fields=(
            ("type", "type"),
            ("amount", "amount"),
            ("date", "date"),
            ("description", "description"),
            ("raw_category", "raw_category"),
            ("is_system", "is_system"),
        )
    )

    class Meta:
        model = Transaction
        fields = ("account", "type", "amount", "date", "description", "raw_category", "is_system")
