from django.db.models import Q, Sum
from django.db.transaction import atomic
from django.utils import timezone
from rest_framework import serializers

from balances.api.services import recalculate_subsequent_balances
from balances.models import BalanceRecord
from transactions.constants import TransactionType
from transactions.models import Transaction


class BalanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceRecord
        fields = ("id", "account", "amount", "date", "note", "created_at")
        read_only_fields = ("id", "created_at")

    @atomic
    def create(self, validated_data):
        date = validated_data["date"]
        account = validated_data["account"]
        new_amount = validated_data["amount"]

        balance_record = BalanceRecord.objects.filter(account=account, date=date).first()
        if balance_record:
            delta = new_amount - balance_record.amount
            balance_record.amount = new_amount
            balance_record.note = validated_data.get("note", "")
            balance_record.save(update_fields=["amount", "note"])
        else:
            prior = BalanceRecord.objects.filter(account=account, date__lt=date).order_by("-date").first()
            prev_day_amount = prior.amount if prior else 0
            agg = Transaction.objects.filter(account=account, date=date, is_system=False).aggregate(
                income=Sum("amount", filter=Q(type=TransactionType.INCOME)),
                expense=Sum("amount", filter=Q(type=TransactionType.EXPENSE)),
            )
            non_system_net = (agg["income"] or 0) - (agg["expense"] or 0)
            delta = new_amount - prev_day_amount - non_system_net
            balance_record = BalanceRecord.objects.create(**validated_data)

        transaction_type = TransactionType.INCOME if delta >= 0 else TransactionType.EXPENSE
        Transaction.objects.create(
            is_system=True,
            account=account,
            amount=abs(delta),
            date=date,
            type=transaction_type,
        )

        recalculate_subsequent_balances(account, date, delta)

        return balance_record

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("The date cannot be in the future.")
        return value

    def validate_account(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("You can only add balance records to your own accounts.")
        return value


class LatestBalanceRecordSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name")

    class Meta:
        model = BalanceRecord
        fields = ("account_id", "account_name", "amount", "date")
