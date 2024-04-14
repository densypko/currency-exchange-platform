from datetime import datetime
from decimal import Decimal
from typing import List, Dict

import requests
from currency_exchange.adapters.base import CurrencyRateAdapter

BASE_URL = "http://data.fixer.io/api/"
ACCESS_KEY = ""  # Replace with your Fixer.io access key

"""
This class is used as code for Provider.adapter_code. This makes providers plug and play.
How to use FixerAdapter:
adapter = FixerAdapter()
return_value = adapter.get_exchange_rates(source_currency, exchange_currencies, valuation_date)
"""


class FixerAdapter(CurrencyRateAdapter):
    def __init__(self, access_key: str = ACCESS_KEY, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_key = access_key

    def get_exchange_rates(self, source_currency_code: str, exchange_currency_codes: List[str], valuation_date: str) -> Dict[str, Decimal]:
        """
        Get exchange rate from Fixer.io and return as Decimal.

        :param source_currency_code: The base currency code.
        :param exchange_currency_codes: The target currency codes.
        :param valuation_date: The date for which to get the exchange rate.
        :return: Exchange rate as Decimal.
        """
        # Validate input
        if not (source_currency_code and exchange_currency_codes):
            raise ValueError("Currency codes cannot be empty.")

        try:
            datetime.strptime(valuation_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("'valuation_date' must be in YYYY-MM-DD format.")

        exchange_currency_codes = ','.join(exchange_currency_codes)
        url = f"{self.base_url}{valuation_date}?access_key={self.access_key}&base={source_currency_code}&symbols={exchange_currency_codes}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()

            # Error handling for response data
            if 'rates' not in data:
                raise ValueError(f"Invalid data received from currency rate service. Info: {data!r}.")

            return data['rates']

        except requests.RequestException as e:
            # Handle any requests-related issues
            raise ConnectionError("Error connecting to Fixer.io service.") from e
        except Exception as e:
            # Handle other exceptions
            raise e
