from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.managers import AccountManager

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager

    from balances.models import BalanceRecord


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=AccountType.choices)
    category = models.CharField(max_length=255, choices=AccountCategory.choices)
    currency = models.CharField(max_length=255, choices=AccountCurrency.choices)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountManager()
    if TYPE_CHECKING:
        balance_records: RelatedManager[BalanceRecord]

    class Meta:
        ordering = ["-created_at"]
        db_table = "accounts"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                condition=models.Q(is_active=True),
                name="unique_active_account_name_per_user",
            )
        ]
        indexes = [models.Index(fields=["type"]), models.Index(fields=["is_active"])]

    def __str__(self):
        """Returns the string representation of the account based on the name."""
        return self.name
