from django.db import models

from .base import TimeAuditedModel
from .currency import Currency


class CurrencyExchangeRate(TimeAuditedModel):
    source_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='exchanges')
    exchange_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, max_digits=18, decimal_places=6)

    def __str__(self):
        return f"{self.source_currency} to {self.exchange_currency} rate: {self.rate_value!r}"
