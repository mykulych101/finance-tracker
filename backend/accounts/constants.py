from django.db import models


class AccountType(models.TextChoices):
    """Defines the types of accounts that can be created in the system."""

    ASSET = "asset", "Asset"
    LIABILITY = "liability", "Liability"
    EQUITY = "equity", "Equity"


class AccountCategory(models.TextChoices):
    """Defines the categories of accounts that can be created in the system."""

    CASH = "cash", "Cash"
    INVESTMENTS = "investments", "Investments"
    REAL_ESTATE = "real_estate", "Real Estate"
    CRYPTO = "crypto", "Crypto"
    CREDIT_CARD = "credit_card", "Credit Card"
    LOAN = "loan", "Loan"
    MORTGAGE = "mortgage", "Mortgage"
    OTHER = "other", "Other"


# UAN/USD/EUR
class AccountCurrency(models.TextChoices):
    """Defines the currencies that can be used for accounts in the system."""

    USD = "USD", "USD"
    EUR = "EUR", "EUR"
    UAN = "UAN", "UAN"
