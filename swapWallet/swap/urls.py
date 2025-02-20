from django.urls import path

from swap.views import CoinBalanceView

urlpatterns = [
    path('coin-balances/', CoinBalanceView.as_view(), name='coin-balances'),
]
