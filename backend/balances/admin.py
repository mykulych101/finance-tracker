from django.contrib import admin

from .models import BalanceRecord


@admin.register(BalanceRecord)
class BalanceRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "amount", "date", "note", "created_at")
    list_filter = ("date", "created_at")
    raw_id_fields = ("account",)
    date_hierarchy = "created_at"
