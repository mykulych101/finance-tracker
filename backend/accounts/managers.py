from django.apps import apps
from django.db import models
from django.db.models import OuterRef, Subquery


class AccountManager(models.Manager):
    def with_latest_balance(self, balance_date=None):
        BalanceRecord = apps.get_model("balances", "BalanceRecord")
        latest_balance_qs = BalanceRecord.objects.filter(account=OuterRef("pk"))

        if balance_date:
            latest_balance_qs = latest_balance_qs.filter(date__lte=balance_date)

        latest_balances = latest_balance_qs.order_by("-date", "-created_at").values("amount")[:1]

        return self.get_queryset().annotate(
            latest_balance=Subquery(latest_balances, output_field=models.DecimalField(max_digits=12, decimal_places=2))
        )
