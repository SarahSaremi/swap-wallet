from django.db import models

from swap.models.coin import Coin
from swap.models.customer import Customer


class Wallet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=50, decimal_places=18, default=0)

    class Meta:
        unique_together = ('customer', 'coin')

    def __str__(self):
        return f'{self.customer.user.username} - {self.coin.name}: {self.balance}'
