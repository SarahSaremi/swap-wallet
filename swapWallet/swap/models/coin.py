from django.db import models


class Coin(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"
