from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.models import Account


class AccountSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name")


class AccountWithBalanceSerializer(AccountSlimSerializer):
    latest_balance = serializers.SerializerMethodField()

    class Meta(AccountSlimSerializer.Meta):
        fields = ("id", "name", "latest_balance")

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_latest_balance(self, obj):
        return obj.latest_balance or 0


class AccountSerializer(AccountWithBalanceSerializer):
    class Meta(AccountWithBalanceSerializer.Meta):
        fields = (
            "id",
            "name",
            "type",
            "category",
            "currency",
            "latest_balance",
            "is_active",
            "created_at",
            "updated_at",
        )


class WriteAccountSerializer(AccountSerializer):
    class Meta(AccountSerializer.Meta):
        fields = ("name", "type", "category", "currency")
        read_only_fields = ("id", "latest_balance", "created_at", "updated_at", "is_active")

    def create(self, validated_data):
        user = self.context["request"].user
        return Account.objects.create(user=user, **validated_data)

    def validate_name(self, value):
        user = self.context["request"].user
        qs = Account.objects.filter(user=user, name=value, is_active=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("You already have an account with this name.")
        return value
