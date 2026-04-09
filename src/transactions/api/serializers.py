from django.db.models import Q, Sum
from django.db.transaction import atomic
from rest_framework import serializers

from accounts.api.serializers import AccountSlimSerializer
from accounts.models import Account
from balances.models import BalanceRecord
from transactions.constants import TransactionType
from transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    account = AccountSlimSerializer(read_only=True)
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.none(), source="account", write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        self.fields["account_id"].queryset = Account.objects.filter(user=user)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "account_id",
            "type",
            "amount",
            "date",
            "description",
            "raw_category",
            "is_system",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_system", "created_at", "updated_at")

    @atomic
    def create(self, validated_data):
        transaction = Transaction.objects.create(**validated_data)
        transaction_date = validated_data["date"]
        account = validated_data["account"]
        transaction_amount = validated_data["amount"]
        transaction_type = validated_data["type"]

        previous_balance_record = (
            BalanceRecord.objects.filter(account=account, date__lt=transaction_date).order_by("-date").first()
        )
        previous_amount = previous_balance_record.amount if previous_balance_record else 0
        delta = transaction_amount if transaction_type == TransactionType.INCOME else -transaction_amount

        balance_record = BalanceRecord.objects.filter(account=account, date=transaction_date).first()
        if balance_record:
            calculated = Transaction.objects.filter(account=account, date=transaction_date).aggregate(
                income=Sum("amount", filter=Q(type=TransactionType.INCOME)),
                expense=Sum("amount", filter=Q(type=TransactionType.EXPENSE)),
            )
            balance_record.amount = previous_amount + (calculated["income"] or 0) - (calculated["expense"] or 0)
            balance_record.save(update_fields=["amount"])
        else:
            BalanceRecord.objects.create(account=account, date=transaction_date, amount=previous_amount + delta)

        self._recalculate_subsequent_balances(account, transaction)

        return transaction

    def _recalculate_subsequent_balances(self, account: Account, transaction: Transaction):
        # Recalculate all balances where date is after transaction date
        subsequent_balance_records = BalanceRecord.objects.filter(account=account, date__gt=transaction.date).order_by(
            "date"
        )
        for record in subsequent_balance_records:
            record.amount += transaction.amount if transaction.type == TransactionType.INCOME else -transaction.amount
            record.save(update_fields=["amount"])
