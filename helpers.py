import os
import requests
import urllib.parse
import json


from flask import redirect, render_template, request, session, g, url_for
from functools import wraps
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


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


def lookup(symbol):
    """Look up quote for symbol."""

    # # Old Contact API
    # try:
    #     api_key = os.environ.get("df78573a-aa22-4502-9ea9-4b92ff5badf6")
    #     url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
    #     response = requests.get(url)
    #     response.raise_for_status()
    # except requests.RequestException:
    #     return None

    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    parameters = {
        'symbol': symbol
    }
    headers = {
        'Accepts':'Application/json',
        'X-CMC_PRO_API_KEY':'df78573a-aa22-4502-9ea9-4b92ff5badf6'
    }
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters).json()
        return {
            'name': response['data'][symbol][0]['name'],
            'price': response['data'][symbol][0]['quote']['USD']['price'],
            'symbol': response['data'][symbol][0]['symbol']
        }
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
