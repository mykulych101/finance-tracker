from django.db.models import Q, Sum

from accounts.models import Account
from balances.models import BalanceRecord
from transactions.constants import TransactionType
from transactions.models import Transaction


def recalculate_balance_on_date(account: Account, date) -> None:
    previous_balance_record = (
        BalanceRecord.objects.select_for_update().filter(account=account, date__lt=date).order_by("-date").first()
    )
    previous_amount = previous_balance_record.amount if previous_balance_record else 0

    balance_record = BalanceRecord.objects.select_for_update().filter(account=account, date=date).first()

    calculated = Transaction.objects.filter(account=account, date=date).aggregate(
        income=Sum("amount", filter=Q(type=TransactionType.INCOME)),
        expense=Sum("amount", filter=Q(type=TransactionType.EXPENSE)),
    )
    date_amount = previous_amount + (calculated["income"] or 0) - (calculated["expense"] or 0)

    if balance_record:
        balance_record.amount = date_amount
        balance_record.save(update_fields=["amount"])
    else:
        BalanceRecord.objects.create(account=account, date=date, amount=date_amount)


def recalculate_subsequent_balances(account: Account, from_date, delta) -> None:
    subsequent_balance_records = list(
        BalanceRecord.objects.select_for_update().filter(account=account, date__gt=from_date).order_by("date")
    )
    for record in subsequent_balance_records:
        record.amount += delta
    BalanceRecord.objects.bulk_update(subsequent_balance_records, ["amount"])
