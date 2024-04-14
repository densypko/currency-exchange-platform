from django.test import TestCase

from ..factories import ProviderFactory, CurrencyFactory, CurrencyExchangeRateFactory
from ...models import Provider, Currency, CurrencyExchangeRate


class TestFactories(TestCase):
    def test_provider(self):
        provider = ProviderFactory()
        self.assertIsInstance(provider, Provider)

    def test_currency(self):
        currency = CurrencyFactory()
        self.assertIsInstance(currency, Currency)

    def test_currency_exchange_rate(self):
        currency_exchange_rate = CurrencyExchangeRateFactory()
        self.assertIsInstance(currency_exchange_rate, CurrencyExchangeRate)
