from django.utils import timezone
from rest_framework import serializers

from balances.models import BalanceRecord


class BalanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceRecord
        fields = ("id", "account", "amount", "date", "note", "created_at")
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        date = validated_data["date"]
        account = validated_data["account"]
        existing_record = BalanceRecord.objects.filter(account=account, date=date).first()
        if existing_record:
            existing_record.amount = validated_data["amount"]
            existing_record.note = validated_data["note"]
            existing_record.save(update_fields=["amount", "note"])
            return existing_record
        return BalanceRecord.objects.create(**validated_data)

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("The date cannot be in the future.")
        return value

    def validate_account(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("You can only add balance records to your own accounts.")
        return value
