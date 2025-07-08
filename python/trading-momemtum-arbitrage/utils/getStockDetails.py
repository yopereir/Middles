import os, requests, json
from dotenv import load_dotenv

load_dotenv()
ALPACA_DATA_URL = os.getenv('ALPACA_DATA_URL','https://data.alpaca.markets/v2')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
if not all([ALPACA_DATA_URL, ALPACA_KEY, ALPACA_SECRET]):
    raise EnvironmentError("One or more Alpaca API environment variables are not set.")

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

def getAskingPrice(ticker: str) -> str:
    return requests.get(f"{ALPACA_DATA_URL}/stocks/quotes/latest?symbols={ticker}", headers=headers).json()['quotes'][ticker]['ap']
