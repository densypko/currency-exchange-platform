from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Dict


class CurrencyRateAdapter(ABC):
    @abstractmethod
    def get_exchange_rates(self, source_currency_code: str, exchange_currency_codes: List[str], valuation_date: str) -> Dict[str, Decimal]:
        """Abstract method to get and save exchange rate."""
        pass
