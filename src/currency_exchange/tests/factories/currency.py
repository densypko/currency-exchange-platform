import factory
from factory.django import DjangoModelFactory

from ...models import Currency


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency

    name = factory.Faker('lexify', text='??????????')
    code = factory.Faker('lexify', text='???')
    symbol = factory.Faker('random_element', elements=('$', '€', '£', '¥'))
