from django.contrib import admin

from .models import Transaction, TransactionImport


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account",
        "type",
        "amount",
        "date",
        "description",
        "raw_category",
        "import_fingerprint",
        "is_system",
        "created_at",
        "updated_at",
    )
    list_filter = ("date", "is_system", "created_at", "updated_at")
    raw_id_fields = ("account",)
    date_hierarchy = "created_at"


@admin.register(TransactionImport)
class TransactionImportAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "file_hash", "imported_at")
    list_filter = ("account", "imported_at")
