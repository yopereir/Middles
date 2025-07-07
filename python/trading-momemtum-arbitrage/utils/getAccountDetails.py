import os, requests, json
from dotenv import load_dotenv

load_dotenv()
ALPACA_ACCOUNT_URL = os.getenv('ALPACA_ACCOUNT_URL')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
if not all([ALPACA_ACCOUNT_URL, ALPACA_KEY, ALPACA_SECRET]):
    raise EnvironmentError("One or more Alpaca API environment variables are not set.")

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

def getAccountBalance() -> str:
    return requests.get(f"{ALPACA_ACCOUNT_URL}/account", headers=headers).json()['buying_power']
