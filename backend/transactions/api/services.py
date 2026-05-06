from balances.api.services import recalculate_balance_on_date, recalculate_subsequent_balances
from transactions.constants import TransactionType
from transactions.models import Transaction


def create_transaction(validated_data) -> Transaction:
    transaction = Transaction.objects.create(**validated_data)
    account = validated_data["account"]
    amount = validated_data["amount"]
    delta = amount if validated_data["type"] == TransactionType.INCOME else -amount

    recalculate_balance_on_date(account, transaction.date)
    recalculate_subsequent_balances(account, transaction.date, delta)

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
        recalculate_balance_on_date(account, new_date)
        recalculate_subsequent_balances(account, new_date, new_delta - old_delta)
    else:
        recalculate_balance_on_date(account, old_date)
        recalculate_subsequent_balances(account, old_date, -old_delta)
        recalculate_balance_on_date(account, new_date)
        recalculate_subsequent_balances(account, new_date, new_delta)

    return instance


def destroy_transaction(instance: Transaction) -> None:
    date = instance.date
    delta = instance.amount if instance.type == TransactionType.INCOME else -instance.amount
    account = instance.account

    instance.delete()

    recalculate_balance_on_date(account, date)
    recalculate_subsequent_balances(account, date, -delta)
