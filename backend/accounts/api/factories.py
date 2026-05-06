import factory

from accounts.constants import AccountCategory, AccountCurrency, AccountType
from accounts.models import Account


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    name = factory.Sequence(lambda n: f"Account-{n:03d}")
    type = factory.Iterator(AccountType.values)
    category = factory.Iterator(AccountCategory.values)
    currency = factory.Iterator(AccountCurrency.values)
    is_active = True
