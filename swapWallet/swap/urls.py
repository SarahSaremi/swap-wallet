from django.urls import path

from swap.views import CoinBalanceView, CoinConversionView, CoinSwapView

urlpatterns = [
    path('coin-balances/', CoinBalanceView.as_view(), name='coin-balances'),
    path('coin-conversion/', CoinConversionView.as_view(), name='coin-conversion'),
    path('coin-swap/', CoinSwapView.as_view(), name='coin-swap'),
]
