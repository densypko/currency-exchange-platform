import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict

from django.db import models

from .base import TimeAuditedModel
from .currency import Currency
from .currency_exchange_rate import CurrencyExchangeRate

logger = logging.getLogger(__name__)


class Provider(TimeAuditedModel):
    name = models.CharField(max_length=64, unique=True)
    priority = models.PositiveIntegerField(
        help_text="The lower the number, the higher the priority.",
        unique=True
    )

    adapter_code = models.TextField(
        help_text="Python code to get the exchange rate."
    )

    def __str__(self):
        return self.name

    def execute_adapter_code(self, context=None):
        if context is None:
            context = {}

        exec(self.adapter_code, context)

        if 'return_value' in context:
            return_value = context['return_value']
            del context['return_value']

            return return_value

    @staticmethod
    def save_exchange_rate_data(source_currency: str, valuation_date: datetime, rate_values: Dict[str, Decimal]):
        logger.debug(f"Saving exchange rates for {source_currency} on {valuation_date}.")

        source_currency = Currency.objects.get(code=source_currency)
        exchange_currencies = Currency.objects.filter(code__in=rate_values.keys()).in_bulk(field_name='code')

        exchange_rates = []
        for exchange_currency_code, rate_value in rate_values.items():
            exchange_currency = exchange_currencies[exchange_currency_code]

            exchange_rate = CurrencyExchangeRate(
                source_currency=source_currency,
                exchange_currency=exchange_currency,
                valuation_date=valuation_date,
                rate_value=rate_value
            )
            exchange_rates.append(exchange_rate)

        # Save exchange rates in bulk
        objs = CurrencyExchangeRate.objects.bulk_create(exchange_rates)

        logger.debug(f"Saved {len(objs)} exchange rates.")

    @staticmethod
    def get_exchange_rate_data(
            source_currency: str,
            exchange_currencies: List[str],
            valuation_date: str,
            provider: 'Provider'
    ) -> Dict[str, Decimal]:

        if isinstance(valuation_date, datetime) or isinstance(valuation_date, date):
            valuation_date = valuation_date.strftime('%Y-%m-%d')

        context = {
            'source_currency': source_currency,
            'exchange_currencies': exchange_currencies,
            'valuation_date': valuation_date,
        }

        return provider.execute_adapter_code(context)
