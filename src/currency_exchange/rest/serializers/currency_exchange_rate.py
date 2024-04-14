from collections import defaultdict

from django.db.models import QuerySet
from rest_framework import serializers

from ...models import CurrencyExchangeRate


class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchangeRate

    @staticmethod
    def group_by_exchange_currency(exchange_rates: QuerySet):
        """
        Group exchange rates by exchange currency.
        :param exchange_rates:
        :return:
        """
        grouped = defaultdict(list)
        for exchange_rate in exchange_rates:
            grouped[exchange_rate.exchange_currency.code].append({
                'rate_value': exchange_rate.rate_value,
                'valuation_date': exchange_rate.valuation_date
            })
        return grouped

    @staticmethod
    def format_rates_as_timeseries(exchange_rates: QuerySet):
        """
        Format exchange rates as timeseries data.
        :param exchange_rates:
        :return:
        """
        timeseries_data = defaultdict(dict)
        for rate in exchange_rates:
            date_key = rate.valuation_date.strftime("%Y-%m-%d")
            currency_code = rate.exchange_currency.code
            timeseries_data[date_key][currency_code] = rate.rate_value

        return timeseries_data
