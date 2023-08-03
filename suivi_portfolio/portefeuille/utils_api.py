import os
from requests import Session
import json
from suivi_portfolio.settings import API_COINMARKET

def get_crypto_prices(model):
    list_crypto = list(model.objects.filter(type_actif='Crypto').values_list('token', flat=True).distinct())
    list_crypto += list(model.objects.filter(token='USDC').values_list('token', flat=True).distinct())

    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest' # Coinmarketcap API url
    api = API_COINMARKET
    crypt = ','.join(map(str, list_crypto))
    stable_USD = ["USDT IMMO"]
    parameters = { 'symbol': crypt, 'convert': 'USD' }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api
    }

    session = Session()
    session.headers.update(headers)

    response = session.get(url, params=parameters)
    
    if response.status_code == 200:
        data = response.json()

        # Extraire les prix de la réponse JSON
        prices = {}
        for crypto_id, crypto_data in data['data'].items():
            # print(crypto_data[0])
            price = crypto_data[0]['quote']['USD']['price']
            prices[crypto_id] = price
            tok = model.objects.get(token=crypto_id)
            tok.unit_price = round(float(crypto_data[0]['quote']['USD']['price']),2)
            tok.value = round(float(crypto_data[0]['quote']['USD']['price'])*float(tok.amount),2)
            tok.save()
            if crypto_id == 'USDC':
                for el in stable_USD:    
                    tok = model.objects.get(token=el)
                    tok.unit_price = round(float(crypto_data[0]['quote']['USD']['price']),2)
                    tok.value = round(float(crypto_data[0]['quote']['USD']['price'])*float(tok.amount),2)
                    tok.save()
    