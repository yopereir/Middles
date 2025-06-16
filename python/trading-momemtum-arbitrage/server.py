import os, requests, math
from datetime import datetime, timedelta
from dotenv import load_dotenv

# LOAD ENVIRONMENT VARIABLES
load_dotenv()
ALPACA_URL = os.getenv('ALPACA_ACCOUNT_URL')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
FEED = os.getenv('ALPACA_FEED', 'indicative')
LIMIT = os.getenv('ALPACA_LIMIT', '10')

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

def is_options_available(ticker_symbol):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker_symbol}?feed={FEED}&limit=1"
    response = requests.get(url, headers=headers)
    return response.status_code == 200 and response.json()['snapshots'] != {}

def add_days_to_date(date, days):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    new_date = date_obj + timedelta(days=days)
    return new_date.strftime('%Y-%m-%d')

# Get valid stock prices
url = "https://data.alpaca.markets/v1beta1/screener/stocks/movers?top="+LIMIT
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("Error fetching stock prices: ", response.status_code)
    exit(1)
gainers = sorted([item for item in response.json().get('gainers', []) if is_options_available(item['symbol'])], key=lambda x: x['percent_change'], reverse=True)
losers = sorted([item for item in response.json().get('losers', []) if is_options_available(item['symbol'])], key=lambda x: x['percent_change'], reverse=True)
if not gainers or not losers:
    print("No gainers or losers data found.")
    exit(1)

# Filtered gainers and losers
print("Top Gainers:")
for item in gainers:
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Price before news: "+ str(item['price']-item['change']))
    print("Strike Price before news: "+ str(math.floor((item['price']-item['change'])*2)/2))
print("\nTop Losers:")
for item in losers:
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Price before news: "+ str(item['price']-item['change']))
    print("Strike Price before news: "+ str(math.ceil((item['price']-item['change'])*2)/2))