from django.db import models


class ExchangeRate(models.Model):
    currency_code_a = models.IntegerField()
    currency_code_b = models.IntegerField()
    monobank_date = models.IntegerField()
    rate_buy = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    rate_sell = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    rate_cross = models.DecimalField(max_digits=20, decimal_places=6, null=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("currency_code_a", "currency_code_b")

    def __str__(self) -> str:
        return f"{self.currency_code_a}/{self.currency_code_b}"
