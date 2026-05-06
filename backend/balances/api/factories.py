import factory

from accounts.api.factories import AccountFactory
from balances.models import BalanceRecord


class BalanceRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BalanceRecord

    account = factory.SubFactory(AccountFactory)
    amount = factory.Faker("pydecimal", left_digits=10, right_digits=2, positive=True)
    date = factory.Faker("date_between", start_date="-1y", end_date="today")
    note = factory.Faker("sentence")
