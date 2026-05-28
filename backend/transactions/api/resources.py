import hashlib
from decimal import Decimal, InvalidOperation

from dateutil.parser import parse as parse_datetime
from django.core.exceptions import ValidationError as DjangoValidationError
from import_export import fields, resources, widgets

from transactions.api.services import create_transaction
from transactions.constants import TransactionType
from transactions.models import Transaction


class DateFromDatetimeWidget(widgets.Widget):
    def clean(self, value, row=None, **kwargs):
        if not str(value or "").strip():
            raise DjangoValidationError("This field is required.")
        try:
            return parse_datetime(str(value), dayfirst=True).date()
        except (ValueError, TypeError) as e:
            msg = f"Invalid date: {value}"
            raise DjangoValidationError(msg) from e

    def render(self, value, obj=None):
        return value.strftime("%d.%m.%Y") if value else ""


class TransactionResource(resources.ModelResource):
    date = fields.Field(
        attribute="date",
        column_name="Date and time",
        widget=DateFromDatetimeWidget(),
    )
    amount = fields.Field(
        attribute="amount",
        column_name="Amount",
        widget=widgets.DecimalWidget(),
    )
    type = fields.Field(
        attribute="type",
        column_name="type",
        widget=widgets.CharWidget(),
    )
    description = fields.Field(
        attribute="description",
        column_name="Description",
        widget=widgets.CharWidget(),
    )
    raw_category = fields.Field(
        attribute="raw_category",
        column_name="Category",
        widget=widgets.CharWidget(),
    )
    import_fingerprint = fields.Field(
        attribute="import_fingerprint",
        column_name="import_fingerprint",
        widget=widgets.CharWidget(),
    )

    class Meta:
        model = Transaction
        import_id_fields = ()
        fields = ("date", "amount", "type", "description", "raw_category", "import_fingerprint")

    def __init__(self, account, **kwargs):
        super().__init__(**kwargs)
        self._account = account

    @staticmethod
    def _compute_fingerprint(row: dict) -> str:
        parts = "|".join(
            [
                str(row.get("Date and time", "")),
                str(row.get("Amount", "")),
                str(row.get("Category", "")),
                str(row.get("Description", "")),
                str(row.get("type", "")),
            ]
        )
        return hashlib.sha256(parts.encode()).hexdigest()

    def before_import(self, dataset, **kwargs):
        super().before_import(dataset, **kwargs)
        self._existing_fingerprints = set(
            Transaction.objects.filter(account=self._account)
            .exclude(import_fingerprint="")
            .values_list("import_fingerprint", flat=True)
        )

    def before_import_row(self, row, **kwargs):
        raw_str = str(row.get("Amount") or "").strip()
        try:
            raw_amount = Decimal(raw_str)
        except InvalidOperation:
            return  # widget will raise the proper ValidationError
        row["type"] = TransactionType.INCOME if raw_amount >= 0 else TransactionType.EXPENSE
        row["Amount"] = str(abs(raw_amount))
        row["import_fingerprint"] = self._compute_fingerprint(row)

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if row["import_fingerprint"] in self._existing_fingerprints:
            return True
        return super().skip_row(instance, original, row, import_validation_errors=import_validation_errors)

    def do_instance_save(self, instance, is_create):
        create_transaction(
            {
                "account": self._account,
                "type": instance.type,
                "amount": instance.amount,
                "date": instance.date,
                "description": instance.description or "",
                "raw_category": instance.raw_category or "",
                "import_fingerprint": instance.import_fingerprint,
            }
        )
        self._existing_fingerprints.add(instance.import_fingerprint)
