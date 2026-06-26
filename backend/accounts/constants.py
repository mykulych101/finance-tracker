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


# UAH/USD/EUR
class AccountCurrency(models.TextChoices):
    """Defines the currencies that can be used for accounts in the system."""

    USD = "USD", "USD"
    EUR = "EUR", "EUR"
    UAH = "UAH", "UAH"


VALID_CATEGORIES_BY_TYPE = {
    AccountType.ASSET: [
        AccountCategory.CASH,
        AccountCategory.INVESTMENTS,
        AccountCategory.REAL_ESTATE,
        AccountCategory.CRYPTO,
        AccountCategory.OTHER,
    ],
    AccountType.LIABILITY: [
        AccountCategory.CREDIT_CARD,
        AccountCategory.LOAN,
        AccountCategory.MORTGAGE,
        AccountCategory.OTHER,
    ],
    AccountType.EQUITY: [AccountCategory.OTHER],
}
