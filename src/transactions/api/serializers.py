from django.db.transaction import atomic
from rest_framework import serializers

from accounts.api.serializers import AccountSlimSerializer
from accounts.models import Account
from transactions.api.services import create_transaction, update_transaction
from transactions.models import Transaction


class BaseTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
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


class ReadTransactionSerializer(BaseTransactionSerializer):
    account = AccountSlimSerializer(read_only=True)

    class Meta(BaseTransactionSerializer.Meta):
        fields = (
            *BaseTransactionSerializer.Meta.fields,
            "account",
        )


class WriteTransactionSerializer(serializers.ModelSerializer):
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), source="account", write_only=True)

    class Meta(BaseTransactionSerializer.Meta):
        fields = (
            *BaseTransactionSerializer.Meta.fields,
            "account_id",
        )

    def validate_account_id(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("Account does not belong to the authenticated user.")
        return value

    @atomic
    def create(self, validated_data):
        return create_transaction(validated_data)

    @atomic
    def update(self, instance, validated_data):
        return update_transaction(instance, validated_data)
