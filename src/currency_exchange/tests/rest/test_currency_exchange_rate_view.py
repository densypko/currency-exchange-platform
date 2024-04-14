from datetime import date, timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from ..factories import ProviderFactory, CurrencyExchangeRateFactory, CurrencyFactory
from ...models import Provider


class TestCurrencyExchangeRateListView(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.refresh = RefreshToken.for_user(self.user)
        self.url = reverse('currency_exchange_rates')
        ProviderFactory(name='Test Provider', priority=1)

    def test_view_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_with_invalid_parameters(self):
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.get(self.url, {'source_currency': 'invalid', 'date_from': '2022-01-30', 'date_to': '2022-01-31'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(self.url, {'source_currency': 'EUR', 'date_from': '2022-01-31', 'date_to': '2022-01-30'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        tomorrow_str = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(self.url, {'source_currency': 'EUR', 'date_from': '2022-01-30', 'date_to': tomorrow_str})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch.object(Provider, 'get_exchange_rate_data', return_value=dict())
    def test_view_with_authentication_and_valid_parameters(self, mock_get_exchange_rate_data):
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.get(self.url, {'source_currency': 'EUR', 'date_from': '2022-02-01', 'date_to': '2022-02-03'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_get_exchange_rate_data.call_count, 3)

    @mock.patch.object(Provider, 'get_exchange_rate_data', return_value=dict())
    def test_view_with_cached_data(self, mock_get_exchange_rate_data):
        CurrencyExchangeRateFactory(
            source_currency=CurrencyFactory(code='EUR'),
            exchange_currency=CurrencyFactory(code='USD'),
            valuation_date='2022-02-01',
        )

        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.get(self.url, {'source_currency': 'EUR', 'date_from': '2022-02-01', 'date_to': '2022-02-03'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_get_exchange_rate_data.call_count, 2)
