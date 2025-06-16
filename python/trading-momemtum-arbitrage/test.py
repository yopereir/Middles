import os, requests
from dotenv import load_dotenv

# LOAD ENVIRONMENT VARIABLES
load_dotenv()
ALPACA_URL = os.getenv('ALPACA_ACCOUNT_URL')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
FEED = os.getenv('ALPACA_FEED', 'indicative')
TICKER = os.getenv('ALPACA_TICKER', 'SOGP')
LIMIT = os.getenv('ALPACA_LIMIT', '1')

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

# SETUP STOCK PRICE REQUEST
url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={TICKER}&apikey={ALPHA_VANTAGE_KEY}&time_from=2025061"
response = requests.get(url, headers=headers)
print(response.json())
