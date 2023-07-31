import os
import requests
import urllib.parse
import json

from flask import redirect, render_template, request, session, jsonify
from config import api_key
from functools import wraps
from random import random, randrange
from requests import Request, Session
from pprint import pprint
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

def top_ten(values):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
    'symbol': "BTC,ETH,USDT,BNB,USDC,BUSD,XRP,DOGE,ADA,MATIC",
    'convert':'USD',
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    # Item endpoints:
    # Convenient ID-based resource endpoints like */quotes/* and */market-pairs/* allow you to bundle several IDs; for example, this allows you to get latest market quotes for a specific set of cryptocurrencies in one call.

    values = []

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)

        print("<------------------------------------------------------------->")
        for i in data["data"]:
            v = data["data"][i]
            name = v["name"]
            symbol = v["symbol"]
            f_price = float(v["quote"]["USD"]["price"])
            if f_price > 0.01:
                price = '%.2f' %f_price
            else:
                price = '%.7f' %f_price
            # print(name, "<-->", symbol,"<-->", price )
            values.append({
                'name': name,
                'symbol': symbol,
                'price': price
                })
        return values
        print("<------------------------------------------------------------->")
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def top_alts(values):
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
    'symbol': "ETH,BNB,XRP,DOGE,ADA,MATIC,DOT,SHIB,TRX,SOL",
    'convert':'USD',
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    # Item endpoints:
    # Convenient ID-based resource endpoints like */quotes/* and */market-pairs/* allow you to bundle several IDs; for example, this allows you to get latest market quotes for a specific set of cryptocurrencies in one call.

    values = []

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        print("<------------------------------------------------------------->")

        for i in data["data"]:
            v = data["data"][i]
            name = v["name"]
            symbol = v["symbol"]
            f_price = float(v["quote"]["USD"]["price"])
            if f_price > 0.01:
                price = '%.2f' %f_price
            else:
                price = '%.7f' %f_price
            # print(name, "<-->", symbol,"<-->", price )
            values.append({
                'name': name,
                'symbol': symbol,
                'price': price
                })
        return values

        # pprint.pprint(f"Bitcoin's test price is: {data}")
        print("<------------------------------------------------------------->")
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def top_memes(values):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
    'symbol': "YOOSHI,SHIB,DOGE,MONA,TAMA,AKITA,KISHU,WOOFY,FLOKI,BABYDOGE",
    'convert':'USD',
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    # Item endpoints:
    # Convenient ID-based resource endpoints like */quotes/* and */market-pairs/* allow you to bundle several IDs; for example, this allows you to get latest market quotes for a specific set of cryptocurrencies in one call.

    values = []

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)

        print("<------------------------------------------------------------->")
        for i in data["data"]:
            v = data["data"][i]
            name = v["name"]
            symbol = v["symbol"]
            f_price = float(v["quote"]["USD"]["price"])
            if f_price > 0.01:
                price = '%.2f' %f_price
            else:
                price = '%.10f' %f_price
            # print(name, "<-->", symbol,"<-->", price )
            values.append({
                'name': name,
                'symbol': symbol,
                'price': price
                })
        return values
        print("<------------------------------------------------------------->")
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def trending(values):
    r = randrange(1,171)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/categories'
    parameters = {
    'start': r,
    'limit': 10,
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    values = []

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)

        print("<------------------------------------------------------------->")
        # pprint(data)
        # for i in data["data"]:
        #     print(i["title"])
        for i in data["data"]:
            unique_id = i["num_tokens"]
            name = i["name"]
            avg_price_change = i["avg_price_change"]
            market_cap = i["market_cap"]
            market_cap_change = i["market_cap_change"]
            volume = i["volume"]

            values.append({
                "id": unique_id,
                "name": name,
                "avg_price_change": avg_price_change,
                "market_cap": market_cap,
                "market_cap_change": market_cap_change,
                "volume": volume,
            })

        # print(values)
        print("<------------------------------------------------------------->")
        return values
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def crypt(value):
    """Format cryptocurrency as USD."""
    return f"${value:,.7f}"

def percent(value):
    """Format percent value"""
    return f"{value:.2f}%"