import os, requests, json
from dotenv import load_dotenv

# LOAD ENVIRONMENT VARIABLES
load_dotenv()
ALPACA_URL = os.getenv('ALPACA_ACCOUNT_URL')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL')
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
    "content-type": "application/json",
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

payload = {
    "symbol": OPTIONS_SYMBOL,
    "qty": 1,
    "side": "sell",                # "buy" or "sell"
    "type": "limit",               # "market", "limit", "stop", etc.
    "limit_price": 0.01,           # Premium to be collected for the option
    "time_in_force": "day",        # "day", "gtc", etc.
    "order_class": "simple",       # Only "simple" supported for now
    "legs": None                   # Required only for multi-leg orders
}

# SETUP STOCK PRICE REQUEST
# Get account balance
response = requests.get(f"{ALPACA_BASE_URL}/account", headers=headers)
remainingBalance = requests.get(f"{ALPACA_BASE_URL}/account", headers=headers).json()['cash']
#response = requests.post(f"{ALPACA_BASE_URL}/options/orders", headers=headers, data=json.dumps(payload))
print(response.json()['cash'], response.status_code)
