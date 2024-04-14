from django import forms

from ..models import Currency


class CurrencyConverterForm(forms.Form):
    source_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), required=True, label='Source Currency')
    target_currencies = forms.ModelMultipleChoiceField(queryset=Currency.objects.all(), required=True, label='Target Currencies')
    amount = forms.FloatField(initial=1, required=True, label='Amount')
