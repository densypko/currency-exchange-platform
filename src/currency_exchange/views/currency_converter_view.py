from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from ..forms import CurrencyConverterForm
from ..models import CurrencyExchangeRate


@staff_member_required
def currency_converter_view(request):
    form = CurrencyConverterForm()
    conversion_results = None

    if request.method == 'POST':
        form = CurrencyConverterForm(request.POST)
        if form.is_valid():
            source_currency = form.cleaned_data['source_currency']
            target_currencies = form.cleaned_data['target_currencies']
            amount = Decimal(form.cleaned_data['amount'])

            exchange_rates = CurrencyExchangeRate.objects.filter(
                source_currency=source_currency,
                exchange_currency__in=target_currencies
            ).order_by('exchange_currency', '-valuation_date').distinct('exchange_currency')

            exchange_rates_dict = {rate.exchange_currency: rate for rate in exchange_rates}

            conversion_results = []
            for target_currency in target_currencies:
                exchange_rate = exchange_rates_dict.get(target_currency)

                if exchange_rate:
                    converted_amount = amount * exchange_rate.rate_value
                    conversion_results.append((source_currency.code, target_currency.code, converted_amount))
                else:
                    conversion_results.append((source_currency.code, target_currency.code, "Not available"))

    return render(request, 'currency_converter.html', {'form': form, 'conversion_results': conversion_results})
