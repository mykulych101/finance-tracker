from django.conf import settings
from django.db import models

from accounts.constants import AccountCategory, AccountCurrency, AccountType


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=AccountType.choices)
    category = models.CharField(max_length=255, choices=AccountCategory.choices)
    currency = models.CharField(max_length=255, choices=AccountCurrency.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "accounts"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        unique_together = ["user", "name"]
        indexes = [models.Index(fields=["type"]), models.Index(fields=["is_active"])]

    def __str__(self):
        """Returns the string representation of the account based on the name."""
        return self.name
