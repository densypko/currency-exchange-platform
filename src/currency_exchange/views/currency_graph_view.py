from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from ..forms import CurrencyConverterForm
from ..models import CurrencyExchangeRate

from ..models import CurrencyExchangeRate
import matplotlib.pyplot as plt
from collections import defaultdict
import io
import urllib, base64

def get_exchange_rate_history(source_currency, target_currency):
    rates = CurrencyExchangeRate.objects.filter(
        source_currency__code=source_currency,
        exchange_currency__code=target_currency
    ).order_by('valuation_date')

    dates = [rate.valuation_date for rate in rates]
    values = [rate.rate_value for rate in rates]

    return dates, values


def plot_exchange_rates(dates, values, source_currency, target_currency):
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker='', color='blue', linewidth=2, label=target_currency)
    plt.title(f'Exchange Rate Evolution: {source_currency} to {target_currency}')
    plt.xlabel('Date')
    plt.ylabel('Exchange Rate')
    plt.legend()

    # Convertir gráfico en imagen para usar en Django
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plt.close(fig)  # Cerrar la figura para liberar memoria
    return uri

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
