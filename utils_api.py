import contextlib
import os
from requests import Session, get
import json
from config import API_COINMARKET, API_VANTAGE
from datetime import datetime
import logging


def get_prices(dataframe):
    # Vérifier si la dernière mise à jour a eu lieu aujourd'hui
        # Extraire les prix des API
    data_bourse = get_quote_bourse(dataframe)
    data_crypto = get_crypto(dataframe)
    data = {**data_bourse, **data_crypto}
    logging.debug(data)
    dataframe['unit_price'] = dataframe['token'].map(data).fillna(dataframe['unit_price'])
    dataframe['value'] = dataframe['unit_price'] * dataframe['amount']
    dataframe['last_update'] = datetime.today().strftime("%Y-%m-%d")
    # for symb, prices in data.items():
    #     tok = model.objects.get(token=symb)
    #     tok.unit_price = round(prices, 5)
    #     tok.value = round(prices*float(tok.amount), 5)
    #     tok.last_update = datetime.now()
    #     tok.save()

    return dataframe


def get_crypto(dataframe):
    """from a list of symbol, connect to the Coin market cap API and extract the quotes
    Args:
        model (Portefeuille)
    Returns:
        QUOTE: dict('symbole' : prices)
    """
    list_crypto = list(dataframe[dataframe['type_actif'] == 'Crypto']['token'].unique())
    list_crypto += list(dataframe[dataframe['token'] == 'USDC']['token'].unique())
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


def get_quote_bourse(dataframe):
    """from a list of symbol, connect to the Vantage API and extract the quotes
    Args:
        dataframe (Portefeuille)
    Returns:
        QUOTE: dict('symbole' : prices)
    """
    list_ = list(dataframe[dataframe['type_actif'] == 'PEA']['token'].unique())
    last_update_list = list(dataframe[dataframe['type_actif'] == 'Crypto']['last_update'])
    list_ += [dataframe[dataframe['token'] == 'EUR']['token'] +'USD']
    last_update_list += list(dataframe[dataframe['token'] == 'EUR']['last_update'].unique())

    api_key = API_VANTAGE
    QUOTE = dict()
    for i, symb in enumerate(list_):
        if last_update_list[i] != datetime.now():
            api_endpoint = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symb}&apikey={api_key}"
            response = get(api_endpoint)
            with contextlib.suppress(Exception):
                data = response.json()
                QUOTE[symb] = float(data.get("Global Quote", {})['05. price'])
    return QUOTE
