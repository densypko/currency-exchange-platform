import logging
from decimal import Decimal

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Provider, CurrencyExchangeRate
from ...models.currency import AVAILABLE_CURRENCIES

logger = logging.getLogger(__name__)


class CurrencyConverterView(APIView):
    # Use JWT authentication
    permission_classes = [IsAuthenticated]

    def _validate_query_parameters(self):
        source_currency = self.request.query_params.get('source_currency')
        amount = self.request.query_params.get('amount')
        exchanged_currency = self.request.query_params.get('exchanged_currency')

        if not all([source_currency, amount, exchanged_currency]):
            raise ValidationError("All parameters (source_currency, amount, exchanged_currency) are mandatory.")

        if source_currency not in AVAILABLE_CURRENCIES or exchanged_currency not in AVAILABLE_CURRENCIES:
            raise ValidationError(
                f"Invalid source_currency or exchanged_currency. "
                f"Available currencies: {AVAILABLE_CURRENCIES!r}."
            )

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0.")
        except ValueError:
            raise ValidationError("Invalid amount.")

        return source_currency, amount, exchanged_currency

    def _retrieve_external_data(self, source_currency: str, valuation_date, exchange_currencies=AVAILABLE_CURRENCIES):
        rate_values = None

        for provider in Provider.objects.all().order_by('priority'):
            try:
                logger.info(f"Retrieving exchange rates for {source_currency} on {valuation_date} from {provider.name!r}.")
                # Pas list of exchange currencies to the provider for optimization api calls
                rate_values = provider.get_exchange_rate_data(
                    source_currency=source_currency,
                    exchange_currencies=exchange_currencies,
                    valuation_date=valuation_date,
                    provider=provider
                )
                if rate_values:
                    # TODO - Save data in a Celery task to avoid blocking the request
                    Provider.save_exchange_rate_data(
                        source_currency=source_currency,
                        valuation_date=valuation_date,
                        rate_values=rate_values
                    )
                    break
            except Exception as e:
                logger.info(f"Error getting exchange rate data from provider {provider.name}: {e}. Trying next provider.")

        return rate_values

    @extend_schema(
        parameters=[
            OpenApiParameter(name='source_currency', type=OpenApiTypes.STR,
                             description="The three-letter currency code of the currency you would like to convert from", required=True),
            OpenApiParameter(name='amount', type=OpenApiTypes.FLOAT,
                             description="The amount to be converted", required=True),
            OpenApiParameter(name='exchanged_currency', type=OpenApiTypes.STR,
                             description="The three-letter currency code of the currency you would like to convert to",
                             required=True),
        ],
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='CurrencyExchangeConvertResponse',
                fields={
                    'query': serializers.DictField(),
                    'rate': serializers.DecimalField(max_digits=18, decimal_places=6),
                    'result': serializers.FloatField(),
                }
            ),
        },
    )
    def get(self, request):
        try:
            source_currency, amount, exchanged_currency = self._validate_query_parameters()
            logger.debug(f"Converting {amount} {source_currency} to {exchanged_currency}.")

            last_currency_exchange_rate = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                exchange_currency__code=exchanged_currency
            ).order_by('-valuation_date').first()

            if not last_currency_exchange_rate:
                rate_values = self._retrieve_external_data(
                    source_currency=source_currency,
                    valuation_date=timezone.now().date(),
                    exchange_currencies=[exchanged_currency]
                )
                rate_value = Decimal(rate_values[exchanged_currency])
            else:
                rate_value = last_currency_exchange_rate.rate_value

            converted_amount = amount * rate_value

            return Response({
                'query': {'from': source_currency, 'to': exchanged_currency, 'amount': amount},
                'rate': rate_value,
                'result': converted_amount
            })

        except ValidationError as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
