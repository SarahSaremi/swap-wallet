import time

from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
from decimal import Decimal
from django.contrib.auth import get_user_model

from swap.models import Coin, Customer, Wallet


class TestCoinSwap(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(self.user)

        self.coin_btc = Coin.objects.create(name="Bitcoin", symbol="BTC")
        self.coin_eth = Coin.objects.create(name="Ethereum", symbol="ETH")
        self.coin_usdt = Coin.objects.create(name="Tether", symbol="USDT")

        self.customer = Customer.objects.create(user=self.user)
        self.balance_btc = Wallet.objects.create(customer=self.customer, coin=self.coin_btc, balance=5.0)
        self.balance_usdt = Wallet.objects.create(customer=self.customer, coin=self.coin_usdt, balance=0.0)

        self.convert_url = reverse('coin-conversion')
        self.swap_url = reverse('coin-swap')

    @patch('requests.get')
    def test_calculate_conversion(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "RAW": {
                "PRICE": 42000.00
            }
        }

        response = self.client.get(self.convert_url,
                                   {'source_coin': 'BTC', 'source_amount': '5', 'destination_coin': 'USDT'})

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertEqual(response_data['conversion_data']['source_coin'], 'BTC')
        self.assertEqual(response_data['conversion_data']['destination_coin'], 'USDT')
        self.assertEqual(Decimal(response_data['conversion_data']['destination_amount']), Decimal(5))

        cache_key = f"{self.customer.id}-5-BTC-USDT"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(Decimal(cached_data['destination_amount']), Decimal(5))

    @patch('requests.get')
    def test_swap_coins_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "RAW": {
                "PRICE": 42000.00
            }
        }

        self.client.get(self.convert_url, {'source_coin': 'BTC', 'source_amount': '5', 'destination_coin': 'USDT'})

        cache_key = f"{self.customer.id}-5-BTC-USDT"

        response = self.client.post(self.swap_url, {
            'source_coin': 'BTC',
            'destination_coin': 'USDT',
            'source_amount': '5',
        })

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertEqual(response_data['message'], 'Conversion successfully confirmed')
        self.assertEqual(Decimal(response_data['destination_amount']), Decimal(5))

        self.balance_btc.refresh_from_db()
        self.balance_usdt.refresh_from_db()
        self.assertEqual(self.balance_btc.balance, 0)
        self.assertEqual(self.balance_usdt.balance, Decimal(5))

        self.assertIsNone(cache.get(cache_key))

    def test_swap_coins_cache_expired(self):
        cache_key = f"{self.customer.id}-5-BTC-USDT"
        expired_conversion_data = {
            "source_amount": "5",
            "destination_amount": "210000.00",
            "source_coin": "BTC",
            "destination_coin": "USDT",
            "rate_at_time": "1.0",
            "timestamp": time.time() - 61
        }
        cache.set(cache_key, expired_conversion_data, timeout=60)

        response = self.client.post(self.swap_url, {
            'source_coin': 'BTC',
            'destination_coin': 'USDT',
            'source_amount': '5',
        })

        self.assertEqual(response.status_code, 400)
        response_data = response.json()

        self.assertEqual(response_data['error'], 'Conversion data has expired, please recalculate.')

    def test_insufficient_funds(self):
        self.balance_btc.balance = Decimal(0)
        self.balance_btc.save()

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "RAW": {
                    "PRICE": 42000.00
                }
            }

            response = self.client.post(self.swap_url, {
                'source_coin': 'BTC',
                'destination_coin': 'USDT',
                'source_amount': '5',
            })

            self.assertEqual(response.status_code, 400)
            response_data = response.json()

            self.assertEqual(response_data['error'], 'Insufficient funds in source coin.')
