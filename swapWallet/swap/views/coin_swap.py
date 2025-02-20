from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
import time

from swap.models import Coin, Wallet


class CoinSwapView(View):

    def post(self, request, *args, **kwargs):
        source_coin_symbol = request.POST.get('source_coin')
        destination_coin_symbol = request.POST.get('destination_coin')
        source_amount = Decimal(request.POST.get('source_amount'))

        cache_key = f"{source_coin_symbol}-{destination_coin_symbol}-{source_amount}"
        conversion_data = cache.get(cache_key)

        if not conversion_data:
            return JsonResponse({"error": "Conversion data has expired, please recalculate."}, status=400)

        elapsed_time = time.time() - conversion_data["timestamp"]
        if elapsed_time > 60:
            return JsonResponse({"error": "Conversion data has expired, please recalculate."}, status=400)

        source_coin = Coin.objects.get(symbol=source_coin_symbol)
        destination_coin = Coin.objects.get(symbol=destination_coin_symbol)

        with transaction.atomic():
            source_balance = Wallet.objects.select_for_update(nowait=True).get(
                customer=request.user.customer, coin=source_coin
            )
            destination_balance = Wallet.objects.select_for_update(nowait=True).get(
                customer=request.user.customer, coin=destination_coin
            )

            if source_balance.balance < source_amount:
                return JsonResponse({"error": "Insufficient funds in source coin."}, status=400)

            source_balance.balance -= source_amount
            destination_balance.balance += Decimal(conversion_data["destination_amount"])

            source_balance.save()
            destination_balance.save()

            cache.delete(cache_key)

        return JsonResponse({
            "message": "Conversion successfully confirmed",
            "source_coin": source_coin_symbol,
            "source_amount": str(source_amount),
            "destination_coin": destination_coin_symbol,
            "destination_amount": conversion_data["destination_amount"]
        })
