import factory

from ...models import Provider


class ProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Provider

    name = factory.Faker('company')
    priority = factory.Sequence(lambda n: n)
    adapter_code = """
def get_exchange_rate(source_currency, exchange_currency, valuation_date):
    # Simulates obtaining exchange rates
    return Decimal('0.85')
"""
