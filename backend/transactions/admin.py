from django.contrib import admin

from transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "account",
        "type",
        "amount",
        "date",
        "description",
        "raw_category",
        "is_system",
        "created_at",
        "updated_at",
    ]
