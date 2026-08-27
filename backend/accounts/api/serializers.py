from decimal import Decimal

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.constants import VALID_CATEGORIES_BY_TYPE, AccountCategory
from accounts.models import Account
from integrations.monobank.converter import convert_amount


class AccountSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name", "currency")


class AccountWithBalanceSerializer(AccountSlimSerializer):
    latest_balance = serializers.SerializerMethodField()

    class Meta(AccountSlimSerializer.Meta):
        fields = ("id", "name", "latest_balance")

    def _convert(self, amount, currency):
        convert_to = self.context.get("convert_to")
        if convert_to and amount:
            amount = convert_amount(amount, currency, convert_to, self.context["rates"])
        field = serializers.DecimalField(max_digits=12, decimal_places=2)
        return field.to_representation(Decimal(str(amount)))

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_latest_balance(self, obj):
        return self._convert(obj.latest_balance or 0, obj.currency)


class AccountSerializer(AccountWithBalanceSerializer):
    credit_limit = serializers.SerializerMethodField()

    class Meta(AccountWithBalanceSerializer.Meta):
        fields = (
            "id",
            "name",
            "type",
            "category",
            "currency",
            "credit_limit",
            "latest_balance",
            "is_active",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True))
    def get_credit_limit(self, obj):
        if obj.credit_limit is None:
            return None
        return self._convert(obj.credit_limit, obj.currency)


class WriteAccountSerializer(AccountSerializer):
    credit_limit = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    class Meta(AccountSerializer.Meta):
        fields = ("name", "type", "category", "currency", "credit_limit")
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

    def validate(self, attrs):
        self._validate_type_and_category(attrs)
        self._validate_category_and_credit_limit(attrs)
        return attrs

    def _validate_type_and_category(self, attrs):
        account_type = attrs.get("type", getattr(self.instance, "type", None))
        account_category = attrs.get("category", getattr(self.instance, "category", None))

        if account_type and account_category:
            allowed = VALID_CATEGORIES_BY_TYPE.get(account_type, set())
            if account_category not in allowed:
                message = f"Category '{account_category}' is not valid for account type '{account_type}'."
                raise serializers.ValidationError(message)

    def _validate_category_and_credit_limit(self, attrs):
        account_category = attrs.get("category", getattr(self.instance, "category", None))
        credit_limit = attrs.get("credit_limit", getattr(self.instance, "credit_limit", None))

        if account_category == AccountCategory.CREDIT_CARD and (credit_limit is None or credit_limit <= 0):
            raise serializers.ValidationError("Credit card accounts must have a positive credit limit.")
        if account_category != AccountCategory.CREDIT_CARD and credit_limit is not None:
            attrs["credit_limit"] = None
