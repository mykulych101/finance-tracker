import factory

from accounts.api.factories import AccountFactory
from transactions.constants import TransactionType
from transactions.models import Transaction


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    account = factory.SubFactory(AccountFactory)
    type = factory.Iterator(TransactionType.values)
    amount = factory.Faker("pydecimal", left_digits=10, right_digits=2, positive=True)
    date = factory.Faker("date_between", start_date="-1y", end_date="today")
    description = factory.Faker("sentence")
    raw_category = factory.Faker("word")
    is_system = False
