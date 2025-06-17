import os, requests
from dotenv import load_dotenv

# LOAD ENVIRONMENT VARIABLES
load_dotenv()
ALPACA_URL = os.getenv('ALPACA_ACCOUNT_URL')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
FEED = os.getenv('ALPACA_FEED', 'indicative')
TICKER = os.getenv('ALPACA_TICKER', 'SATS')
LIMIT = os.getenv('ALPACA_LIMIT', '1')
EXPIRATION_DATE="2025-06-20"
STRIKE_PRICE=17
OPTIONS_SYMBOL = "RUN250620C00010000"

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

# SETUP STOCK PRICE REQUEST
url = f"https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={OPTIONS_SYMBOL}&feed=indicative"
response = requests.get(url, headers=headers)
optionQuoteDetails = response.json()['quotes'][OPTIONS_SYMBOL]
print(abs(optionQuoteDetails['bp'] + optionQuoteDetails['ap'])/2)
print(response.json(), response.status_code)
