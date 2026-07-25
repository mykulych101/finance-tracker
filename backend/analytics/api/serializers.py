from rest_framework import serializers

from accounts.api.serializers import AccountWithBalanceSerializer


class AnalyticsNetWorthSerializer(serializers.Serializer):
    net_worth = serializers.DecimalField(max_digits=20, decimal_places=2, coerce_to_string=False)
    assets_total = serializers.DecimalField(max_digits=20, decimal_places=2, coerce_to_string=False)
    liabilities_total = serializers.DecimalField(max_digits=20, decimal_places=2, coerce_to_string=False)
    accounts = AccountWithBalanceSerializer(many=True)


class AnalyticsNetWorthHistoryItemSerializer(serializers.Serializer):
    date = serializers.DateField()
    net_worth = serializers.DecimalField(max_digits=14, decimal_places=2, coerce_to_string=False)
    assets = serializers.DecimalField(max_digits=14, decimal_places=2, coerce_to_string=False)
    liabilities = serializers.DecimalField(max_digits=14, decimal_places=2, coerce_to_string=False)
