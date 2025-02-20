from django.core.cache import cache
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
import time

from swap.utils import get_usd_price


class CoinConversionView(View):
    CACHE_TIMEOUT = 60  # Cache timeout: 1 minute

    def get(self, request, *args, **kwargs):
        source_coin_symbol = request.GET.get('source_coin')
        source_amount = Decimal(request.GET.get('source_amount'))
        destination_coin_symbol = request.GET.get('destination_coin')

        source_usd_price = get_usd_price(source_coin_symbol)
        destination_usd_price = get_usd_price(destination_coin_symbol)

        conversion_rate = Decimal(source_usd_price / destination_usd_price)
        destination_amount = source_amount * conversion_rate

        cache_key = f"{source_coin_symbol}-{destination_coin_symbol}-{source_amount}"

        conversion_data = {
            "source_amount": str(source_amount),
            "destination_amount": str(destination_amount),
            "source_coin": source_coin_symbol,
            "destination_coin": destination_coin_symbol,
            "rate_at_time": str(conversion_rate),
            "timestamp": time.time()
        }
        cache.set(cache_key, conversion_data, timeout=self.CACHE_TIMEOUT)

        return JsonResponse({
            "message": "Conversion calculated",
            "conversion_data": conversion_data
        })

