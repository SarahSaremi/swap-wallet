from time import sleep

from django.contrib.auth.models import User
from django.test import Client
from decimal import Decimal

from django.urls import reverse

from swap.models import Coin, Customer, Wallet


def populate_data():
    coins = {
        ("USDT", "Tether", '100'),
        ("BTC", "Bitcoin", "0.00001"),
        ("ETH", "Ethereum", "0.0002"),
        ("DOGE", "Dogecoin", "10"),
        ("XRP", "Ripple", "50.2322"),
    }
    for coin_symbol, coin_name, _ in coins:
        Coin.objects.get_or_create(symbol=coin_symbol, name=coin_name)

    user, _ = User.objects.get_or_create(username="customer1", email="customer1@example.com", password="password123")
    customer, _ = Customer.objects.get_or_create(user=user)

    for coin_symbol, _, amount in coins:
        coin = Coin.objects.get(symbol=coin_symbol)
        wallet, _ = Wallet.objects.get_or_create(customer=customer, coin=coin)
        wallet.balance = Decimal(amount)
        wallet.save()

    print("Database populated with coins and customer.")
    return user


def call_conversion_api(user):
    client = Client()
    client.force_login(user)

    response = client.get(reverse('coin-balances'))
    print("Get customer balance:", response.json())

    response = client.get(reverse('coin-conversion'), {
        'source_coin': 'BTC',
        'destination_coin': 'USDT',
        'source_amount': '0.000010',
    })
    print("Conversion API Response (BTC to USDT):", response.json())

    sleep(30)
    response = client.post(reverse('coin-swap'), {
        'source_coin': 'BTC',
        'destination_coin': 'USDT',
        'source_amount': '0.000010',
    })
    print("Swap API Response (BTC to USDT):", response.json())


user = populate_data()
call_conversion_api(user)
