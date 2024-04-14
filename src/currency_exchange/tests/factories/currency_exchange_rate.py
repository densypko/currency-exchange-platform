from datetime import date

import factory
from factory.django import DjangoModelFactory

from .currency import CurrencyFactory
from ...models import CurrencyExchangeRate


class CurrencyExchangeRateFactory(DjangoModelFactory):
    class Meta:
        model = CurrencyExchangeRate

    source_currency = factory.SubFactory(CurrencyFactory)
    exchange_currency = factory.SubFactory(CurrencyFactory)
    valuation_date = date.today()
    rate_value = factory.Faker('pydecimal', left_digits=12, right_digits=6)
