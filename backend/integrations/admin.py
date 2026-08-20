from django.contrib import admin

from .models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "currency_code_a",
        "currency_code_b",
        "monobank_date",
        "rate_buy",
        "rate_sell",
        "rate_cross",
        "fetched_at",
    )
    list_filter = ("fetched_at",)
