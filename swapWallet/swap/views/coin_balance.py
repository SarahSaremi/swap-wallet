from decimal import Decimal

from django.http import JsonResponse
from django.views import View

from swap.models import Wallet
from swap.utils import get_usd_price

DECIMAL_PLACES = 6


class CoinBalanceView(View):
    def get(self, request, *args, **kwargs):
        customer = request.user.customer

        coin_balances = []

        for balance in Wallet.objects.filter(customer=customer):
            coin = balance.coin
            coin_symbol = coin.symbol
            coin_balance = balance.balance

            try:
                usd_price = get_usd_price(coin_symbol)
                coin_value_usd = coin_balance * Decimal(usd_price)
            except Exception as e:
                return JsonResponse({"error": f"Error fetching price for {coin_symbol}: {str(e)}"}, status=400)

            coin_balances.append({
                "coin": coin_symbol,
                "balance": str(round(coin_balance, DECIMAL_PLACES)),
                "usd_value": str(round(coin_value_usd, DECIMAL_PLACES)),
            })

        return JsonResponse({"coin_balances": coin_balances}, status=200)
