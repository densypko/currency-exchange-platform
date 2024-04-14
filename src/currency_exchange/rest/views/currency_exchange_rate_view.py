import logging
from datetime import timedelta, datetime

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import CurrencyExchangeRateSerializer
from ...models import CurrencyExchangeRate, Provider
from ...models.currency import AVAILABLE_CURRENCIES

logger = logging.getLogger(__name__)


class CurrencyExchangeRateListView(generics.ListAPIView):
    # Use JWT authentication
    permission_classes = [IsAuthenticated]

    def _validate_query_parameters(self):
        source_currency = self.request.query_params.get('source_currency')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        # Check for mandatory parameters
        if not all([source_currency, date_from, date_to]):
            raise ValidationError("All parameters (source_currency, date_from, date_to) are mandatory.")

        if source_currency not in AVAILABLE_CURRENCIES:
            raise ValidationError(
                f"Invalid source_currency: {source_currency!r}. "
                f"Available currencies: {AVAILABLE_CURRENCIES!r}."
            )

        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("Dates must be in 'YYYY-MM-DD' format.")

        today = timezone.now().date()
        if date_to > today:
            raise ValidationError("'date_to' cannot be later than today's date.")

        if date_from > date_to:
            raise ValidationError("'date_from' cannot be later than 'date_to'.")

        return source_currency, date_from, date_to

    def _filter_queryset_by_date(self, source_currency, date_from, date_to):
        # TODO - Pass date_from and date_to to django_filters.rest_framework.DjangoFilterBackend
        return CurrencyExchangeRate.objects.filter(
            source_currency__code=source_currency,
            valuation_date__range=[date_from, date_to]
        ).select_related('exchange_currency')

    def _fill_missing_data(self, queryset, source_currency, date_from, date_to):
        existing_dates = set(queryset.order_by('valuation_date').values_list('valuation_date', flat=True))
        logger.debug(f"Filled missing data for {source_currency} from {date_from} to {date_to}.")
        logger.debug(f"Existing dates: {existing_dates}.")

        current_date = date_from
        while current_date <= date_to:
            if current_date not in existing_dates:
                self._retrieve_external_data(source_currency, current_date)
            current_date += timedelta(days=1)

    def _retrieve_external_data(self, source_currency, valuation_date):
        rate_values = None
        for provider in Provider.objects.all().order_by('priority'):
            try:
                logger.info(f"Retrieving exchange rates for {source_currency} on {valuation_date} from {provider.name!r}.")
                # Pas list of exchange currencies to the provider for optimization api calls
                rate_values = Provider.get_exchange_rate_data(
                    source_currency=source_currency,
                    exchange_currencies=AVAILABLE_CURRENCIES,
                    valuation_date=valuation_date,
                    provider=provider
                )
                if rate_values:
                    logger.debug(f"Saving exchange rates for {source_currency} on {valuation_date}.")
                    # TODO - Save data in a Celery task to avoid blocking the request
                    Provider.save_exchange_rate_data(
                        source_currency=source_currency,
                        valuation_date=valuation_date,
                        rate_values=rate_values
                    )
                    break
            except Exception as ex:
                logger.info(f"Error getting exchange rate data from provider {provider.name!r}: {ex}. Trying next provider.")

        return rate_values

    def get_queryset(self):
        """
        Retrieves a queryset of CurrencyExchangeRate objects filtered by
        mandatory source_currency, date_from, and date_to query parameters.
        """
        source_currency, date_from, date_to = self._validate_query_parameters()
        queryset = self._filter_queryset_by_date(source_currency, date_from, date_to)

        self._fill_missing_data(queryset, source_currency, date_from, date_to)

        return queryset.order_by('exchange_currency', 'valuation_date')

    def list(self, request, *args, **kwargs):
        """
        Handles the GET request.
        Returns a list of exchange rates grouped by date.
        """
        try:
            logger.debug(f"Starting to retrieve exchange rates from the database.")
            queryset = self.get_queryset()
            grouped_rates = CurrencyExchangeRateSerializer.format_rates_as_timeseries(queryset)
            return Response(grouped_rates)
        except ValidationError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='source_currency', type=OpenApiTypes.STR, description="The three-letter currency code of the currency",
                             required=True),
            OpenApiParameter(name='date_from', type=OpenApiTypes.STR, description="Range start date. Format: 'YYYY-MM-DD'", required=True),
            OpenApiParameter(name='date_to', type=OpenApiTypes.STR, description="End date of range. Format: 'YYYY-MM-DD'", required=True),
        ],
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='CurrencyExchangeRateResponse',
                fields={
                    '2023-12-01': inline_serializer(
                        name='ExchangeRates',
                        fields={
                            'currency_code': serializers.CharField(),
                            'rate_value': serializers.DecimalField(max_digits=18, decimal_places=6)
                        },
                        many=True
                    )
                }
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
