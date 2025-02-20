import requests

CRYPTO_COMPARE_URL = "https://min-api.cryptocompare.com/data/generateAvg?fsym={}&tsym=USD&e=coinbase"


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
