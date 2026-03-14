from rest_framework import serializers

from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name", "type", "category", "currency", "is_active", "created_at", "updated_at")
        read_only_fields = ["id", "created_at", "updated_at", "is_active"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Account.objects.create(user=user, **validated_data)

    def validate_name(self, value):
        user = self.context["request"].user
        if Account.objects.filter(user=user, name=value, is_active=True).exists():
            raise serializers.ValidationError("You already have an account with this name.")
        return value
