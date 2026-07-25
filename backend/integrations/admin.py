from django.contrib import admin

from integrations.models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = (
        "currency_code_a",
        "currency_code_b",
        "rate_buy",
        "rate_sell",
        "rate_cross",
        "monobank_date",
        "fetched_at",
    )
    ordering = ("currency_code_a", "currency_code_b")
