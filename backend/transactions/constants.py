from django.db import models


class TransactionType(models.TextChoices):
    """Defines the types of transactions that can be recorded in the system."""

    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"
