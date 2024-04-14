import random
from datetime import datetime
from decimal import Decimal
from typing import List, Dict

from currency_exchange.adapters.base import CurrencyRateAdapter
from currency_exchange.models.currency import AVAILABLE_CURRENCIES


class MockAdapter(CurrencyRateAdapter):
    def __init__(self):
        self.available_currencies = AVAILABLE_CURRENCIES

    def _generate_mock_rates(self, source_currency: str):
        """
        Generate mock exchange rates for a given currency.
        """
        rates = {}
        for currency in self.available_currencies:
            if currency != source_currency:
                rates[currency] = Decimal(random.uniform(0.5, 1.5)).quantize(Decimal('.0001'))
        return rates

    def get_exchange_rates(self, source_currency_code: str, exchange_currency_codes: List[str], valuation_date: str) -> Dict[str, Decimal]:
        """
        Simulate getting exchange rates for a given date and return as Decimal.

        :param source_currency_code: The base currency code.
        :param exchange_currency_codes: The target currency codes.
        :param valuation_date: The date for which to get the exchange rate.
        :return: Exchange rates as Decimal.
        """
        if not (source_currency_code and exchange_currency_codes):
            raise ValueError("Currency codes cannot be empty.")

        try:
            datetime.strptime(valuation_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("'valuation_date' must be in YYYY-MM-DD format.")

        if source_currency_code not in self.available_currencies:
            raise ValueError(f"Invalid source currency: {source_currency_code}")

        mock_rates = self._generate_mock_rates(source_currency_code)

        filtered_rates = {code: mock_rates.get(code, Decimal('0.0')) for code in exchange_currency_codes}

        return filtered_rates
