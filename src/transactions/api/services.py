from django.db.models import Q, Sum

from accounts.models import Account
from balances.models import BalanceRecord
from transactions.constants import TransactionType
from transactions.models import Transaction


def create_transaction(validated_data) -> Transaction:
    transaction = Transaction.objects.create(**validated_data)
    account = validated_data["account"]
    amount = validated_data["amount"]
    delta = amount if validated_data["type"] == TransactionType.INCOME else -amount

    _recalculate_balance_on_date(account, transaction.date)
    _recalculate_subsequent_balances(account, transaction.date, delta)

    return transaction


def update_transaction(instance: Transaction, validated_data) -> Transaction:
    old_date = instance.date
    old_delta = instance.amount if instance.type == TransactionType.INCOME else -instance.amount

    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()

    new_date = instance.date
    new_delta = instance.amount if instance.type == TransactionType.INCOME else -instance.amount
    account = instance.account

    if old_date == new_date:
        _recalculate_balance_on_date(account, new_date)
        _recalculate_subsequent_balances(account, new_date, new_delta - old_delta)
    else:
        _recalculate_balance_on_date(account, old_date)
        _recalculate_subsequent_balances(account, old_date, -old_delta)
        _recalculate_balance_on_date(account, new_date)
        _recalculate_subsequent_balances(account, new_date, new_delta)

    return instance


def destroy_transaction(instance: Transaction) -> None:
    date = instance.date
    delta = instance.amount if instance.type == TransactionType.INCOME else -instance.amount
    account = instance.account

    instance.delete()

    _recalculate_balance_on_date(account, date)
    _recalculate_subsequent_balances(account, date, -delta)


def _recalculate_balance_on_date(account: Account, date) -> None:
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


def _recalculate_subsequent_balances(account: Account, from_date, delta) -> None:
    subsequent_balance_records = list(
        BalanceRecord.objects.select_for_update().filter(account=account, date__gt=from_date).order_by("date")
    )
    for record in subsequent_balance_records:
        record.amount += delta
    BalanceRecord.objects.bulk_update(subsequent_balance_records, ["amount"])
