import secrets
from decimal import Decimal

import factory

from accounts.constants import VALID_CATEGORIES_BY_TYPE, AccountCategory, AccountCurrency, AccountType
from accounts.models import Account


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    name = factory.Sequence(lambda n: f"Account-{n:03d}")
    type = factory.Iterator(AccountType.values)
    currency = factory.Iterator(AccountCurrency.values)
    is_active = True

    @factory.lazy_attribute
    def category(self):
        return secrets.choice(VALID_CATEGORIES_BY_TYPE[self.type])

    @factory.lazy_attribute
    def credit_limit(self):
        if self.category == AccountCategory.CREDIT_CARD:
            return Decimal("1000.00")
        return None
