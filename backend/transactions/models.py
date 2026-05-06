from django.db import models

from accounts.models import Account
from transactions.constants import TransactionType


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    raw_category = models.CharField(max_length=255, blank=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        db_table = "transactions"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [models.Index(fields=["date"]), models.Index(fields=["account"])]

    def __str__(self):
        """Returns the string representation of the transaction based on the account name and date."""
        return f"{self.account.name} - {self.date}"
