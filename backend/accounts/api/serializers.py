from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "type",
            "category",
            "currency",
            "current_balance",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "current_balance", "created_at", "updated_at", "is_active")

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_current_balance(self, obj):
        latest = obj.balance_records.order_by("-date").first()
        return latest.amount if latest else 0

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


class AccountSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name")
