import contextlib
import os
from requests import Session, get
import json
from datetime import datetime
import logging
import streamlit as st
import pandas as pd
import sqlite3

API_COINMARKET = os.environ["API_COINMARKET"]
API_VANTAGE = os.environ["API_VANTAGE"]


def connect_to_database(db, table):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    data = cursor.execute(f"SELECT * FROM {table} where id_user = '{st.session_state['username']}'")
    df_total = pd.DataFrame(data, columns=[x[0] for x in cursor.description])
    conn.close()
    return df_total

def get_prices(dataframe):
    # Vérifier si la dernière mise à jour a eu lieu aujourd'hui
        # Extraire les prix des API
    data_bourse = get_quote_bourse(dataframe)
    data_crypto = get_crypto(dataframe)
    data = {**data_bourse, **data_crypto}
    logging.debug(data)
    dataframe['unit_price'] = dataframe['token'].map(data).fillna(dataframe['unit_price'])
    dataframe['value'] = dataframe['unit_price'] * dataframe['amount']
    dataframe['last_update'] = datetime.today().date().strftime("%Y-%m-%d")
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


def update_prices(dataframe):
    """Update the prices of the Portefeuille in db"""
    print('='*50)
    print("IN UPGRADE")
    print(dataframe)
    print('='*50)
    df_last = dataframe[dataframe["id_portefeuille"] == max(dataframe["id_portefeuille"])]
    df_last = get_prices(df_last)

    df_last["id_portefeuille"] = df_last["id_portefeuille"].apply(lambda x: x + 1)
    df_last["last_update"] = pd.to_datetime(df_last["last_update"], format="mixed")
    df_last["id"] = df_last["id"].apply(lambda x: x + len(df_last) + 1)

    return df_last
