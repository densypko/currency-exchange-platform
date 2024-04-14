from django.contrib import admin

from ..models import CurrencyExchangeRate


@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('source_currency', 'exchange_currency', 'valuation_date', 'rate_value',)
    list_filter = ('source_currency', 'exchange_currency', 'valuation_date',)
    search_fields = ('source_currency__name', 'exchange_currency__name',)
    ordering = ('valuation_date',)

    fieldsets = (
        (None, {
            'fields': ('source_currency', 'exchange_currency', 'valuation_date', 'rate_value',)
        }),
    )
