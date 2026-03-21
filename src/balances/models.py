from django.db import models

from accounts.models import Account


class BalanceRecord(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="balance_records")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        db_table = "balance_records"
        verbose_name = "Balance Record"
        verbose_name_plural = "Balance Records"
        indexes = [models.Index(fields=["date"]), models.Index(fields=["account"])]

    def __str__(self):
        """Returns the string representation of the balance record based on the account name and date."""
        return f"{self.account.name} - {self.date}"
