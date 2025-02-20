from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
import json

from swap.models import Coin, Customer, Wallet

USD_PRICE = 42000.00


class TestCoinBalanceView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(self.user)
        self.customer = Customer.objects.create(user=self.user)

        self.coin_btc = Coin.objects.create(name="Bitcoin", symbol="BTC")
        self.coin_eth = Coin.objects.create(name="Ethereum", symbol="ETH")

        self.balance_btc = Wallet.objects.create(customer=self.customer, coin=self.coin_btc, balance=1.5)
        self.balance_eth = Wallet.objects.create(customer=self.customer, coin=self.coin_eth, balance=10.0)

        self.url = reverse('coin-balances')

    @patch('requests.get')
    def test_coin_balances(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "RAW": {
                "PRICE": USD_PRICE
            }
        }

        response = self.client.get(self.url)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response_data['coin_balances']), 2)
        self.assertEqual(response_data['coin_balances'][0]['coin'], 'BTC')
        self.assertEqual(Decimal(response_data['coin_balances'][0]['balance']), Decimal(1.5))
        self.assertEqual(Decimal(response_data['coin_balances'][0]['usd_value']), Decimal(1.5) * Decimal(USD_PRICE))

        self.assertEqual(response_data['coin_balances'][1]['coin'], 'ETH')
        self.assertEqual(Decimal(response_data['coin_balances'][1]['balance']), Decimal(10))
        self.assertEqual(Decimal(response_data['coin_balances'][1]['usd_value']), Decimal(10) * Decimal(USD_PRICE))

    @patch('requests.get')
    def test_coin_balances_error_fetching_price(self, mock_get):
        mock_get.return_value.status_code = 500

        response = self.client.get(self.url)

        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Error fetching price", response_data['error'])

