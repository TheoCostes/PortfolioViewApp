import contextlib
import os
from django.utils import timezone
from requests import Session, get
import json
from suivi_portfolio.settings import API_COINMARKET, API_VANTAGE


def get_prices(model):
    objet_modele = model.objects.get(id=1)

    # Vérifier si la dernière mise à jour a eu lieu aujourd'hui
        # Extraire les prix des API
    data_bourse = get_quote_bourse(model)
    data_crypto = get_crypto(model)
    data = {**data_bourse, **data_crypto}
    for symb, prices in data.items():
        tok = model.objects.get(token=symb)
        tok.unit_price = round(prices, 2)
        tok.value = round(prices*float(tok.amount), 2)
        tok.last_update = timezone.now()
        tok.save()


def get_crypto(model):
    """from a list of symbol, connect to the Coin market cap API and extract the quotes
    Args:
        model (Portefeuille)
    Returns:
        QUOTE: dict('symbole' : prices)
    """
    list_crypto = list(model.objects.filter(
        type_actif='Crypto').values_list('token', flat=True).distinct())
    list_crypto += list(model.objects.filter(token='USDC')
                        .values_list('token', flat=True).distinct())
    stable_USD = ["USDT IMMO", "USDT TRADING"]

    # Coinmarketcap API url
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    api = API_COINMARKET
    crypt = ','.join(map(str, list_crypto))
    parameters = {'symbol': crypt, 'convert': 'USD'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api
    }

    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    if response.status_code == 200:
        data = response.json()
        Quote = dict()
        for crypto_id, crypto_data in data['data'].items():
            Quote[crypto_id] = float(crypto_data[0]['quote']['USD']['price'])
            if crypto_id == 'USDC':
                for el in stable_USD:
                    Quote[el] = float(crypto_data[0]['quote']['USD']['price'])
        return Quote


def get_quote_bourse(model):
    """from a list of symbol, connect to the Vantage API and extract the quotes
    Args:
        model (Portefeuille)
    Returns:
        QUOTE: dict('symbole' : prices)
    """
    list_ = list(model.objects.filter(type_actif='PEA').values_list(
        'token', flat=True).distinct())
    last_update_list = list(model.objects.filter(type_actif='PEA').values_list(
        'last_update', flat=True))
    list_ += [model.objects.filter(token='EUR').values('token')[0]['token']+'USD']
    last_update_list += list(model.objects.filter(token='EUR').values_list(
        'last_update', flat=True).distinct())
    print(list_)
    print(len(list_), len(last_update_list))
    api_key = API_VANTAGE
    QUOTE = dict()
    for i, symb in enumerate(list_):
        print(last_update_list[i], timezone.now())
        if last_update_list[i] != timezone.now():
            api_endpoint = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symb}&apikey={api_key}"
            response = get(api_endpoint)
            with contextlib.suppress(Exception):
                data = response.json()
                QUOTE[symb] = float(data.get("Global Quote", {})['05. price'])
    return QUOTE
