from django.contrib import admin

from balances.models import BalanceRecord


@admin.register(BalanceRecord)
class BalanceRecordAdmin(admin.ModelAdmin):
    list_display = ["account", "amount", "date", "note", "created_at"]
    list_filter = ["date", "account"]
    search_fields = ["account__name", "note"]
    ordering = ["-date", "-created_at"]
