from django.db import models

AVAILABLE_CURRENCIES = ['EUR', 'CHF', 'USD', 'GBP']


class Currency(models.Model):
    name = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=3, unique=True)
    symbol = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name
