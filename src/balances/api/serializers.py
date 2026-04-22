from django.db.transaction import atomic
from django.utils import timezone
from rest_framework import serializers

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

        # Create balance record
        balance_record = BalanceRecord.objects.filter(account=account, date=date).first()
        if balance_record:
            transaction_type = (
                TransactionType.INCOME if validated_data["amount"] >= balance_record.amount else TransactionType.EXPENSE
            )
            balance_record.amount = validated_data["amount"]
            balance_record.note = validated_data["note"]
            balance_record.save(update_fields=["amount", "note"])
        else:
            balance_record = BalanceRecord.objects.create(**validated_data)
            transaction_type = TransactionType.INCOME if validated_data["amount"] >= 0 else TransactionType.EXPENSE

        # Create transaction
        Transaction.objects.create(
            is_system=True,
            account=account,
            amount=validated_data["amount"],
            date=date,
            type=transaction_type,
        )

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
