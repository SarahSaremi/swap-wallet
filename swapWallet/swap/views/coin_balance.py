import requests
from django.http import JsonResponse
from django.views import View

from swap.models import Wallet

CRYPTO_COMPARE_URL = "https://min-api.cryptocompare.com/data/generateAvg?fsym={coin_symbol}&tsym=USD&e=coinbase"


class CoinBalanceView(View):
    def get(self, request, *args, **kwargs):
        customer = request.user.customer

        coin_balances = []

        for balance in Wallet.objects.filter(customer=customer):
            coin = balance.coin
            coin_symbol = coin.symbol
            coin_balance = balance.balance

            try:
                usd_price = self.get_usd_price(coin_symbol)
                coin_value_usd = coin_balance * usd_price
            except Exception as e:
                return JsonResponse({"error": f"Error fetching price for {coin_symbol}: {str(e)}"}, status=400)

            coin_balances.append({
                "coin": coin_symbol,
                "balance": str(coin_balance),
                "usd_value": round(coin_value_usd, 2),
            })

        return JsonResponse({"coin_balances": coin_balances}, status=200)

    @staticmethod
    def get_usd_price(coin_symbol: str):
        url = CRYPTO_COMPARE_URL.format(coin_symbol)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            try:
                price = data['RAW']['PRICE']
                return price
            except KeyError:
                raise ValueError(f"Price not found for {coin_symbol}")
        else:
            raise ValueError(f"Failed to fetch data for {coin_symbol}")
