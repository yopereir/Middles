import os, requests, math
from datetime import datetime, timedelta, date
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

def is_option_available(item, call_or_put='C'):
    symbol = item['symbol']
    expirationDate = get_nearest_friday()
    strikePrice = str(math.floor((item['price']-item['change'])*2)/2)
    optionSymbol = get_option_code(symbol, call_or_put, float(strikePrice), expirationDate)
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots?symbols={optionSymbol}&feed={FEED}&limit=1"
    response = requests.get(url, headers=headers)
    return response.status_code == 200 and response.json()['snapshots'] != {}

def get_nearest_friday():
    today = date.today()
    weekday = today.weekday()
    days_until_friday = (4 - weekday) % 7
    nearest_friday = today + timedelta(days=days_until_friday)
    return nearest_friday.strftime("%Y-%m-%d")

def get_option_code(symbol='AAPL', call_or_put='C', strike_price=123.45, expiration_date="2025-06-20"):
    root = symbol  # pad with spaces to 6 chars
    date_part = expiration_date.replace('-', '')[2:]  # get YYMMDD
    cp = call_or_put.upper()
    strike = int(round(strike_price * 1000))  # convert to integer with 3 decimal precision
    strike_part = f"{strike:08d}"

    return f"{root}{date_part}{cp}{strike_part}"

# Get valid stock prices
url = "https://data.alpaca.markets/v1beta1/screener/stocks/movers?top="+LIMIT
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("Error fetching stock prices: ", response.status_code)
    exit(1)
gainers = sorted([item for item in response.json().get('gainers', []) if is_option_available(item, 'P')], key=lambda x: x['percent_change'], reverse=True)
losers = sorted([item for item in response.json().get('losers', []) if is_option_available(item, 'C')], key=lambda x: x['percent_change'], reverse=True)
if not gainers and not losers:
    print("No gainers or losers data found.")
    exit(1)

# Filtered gainers and losers
print("Top Gainers:")
for item in gainers:
    symbol = item['symbol']
    expirationDate = get_nearest_friday()
    strikePrice = str(math.floor((item['price']-item['change'])*2)/2)
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Strike Price before news: "+ strikePrice)
    print("Max Expiration Date: "+ expirationDate)
    print(f"Option code: {get_option_code(symbol, 'P', float(strikePrice), expirationDate)}")
print("\nTop Losers:")
for item in losers:
    symbol = item['symbol']
    expirationDate = get_nearest_friday()
    strikePrice = str(math.ceil((item['price']-item['change'])*2)/2)
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Price before news: "+ str(item['price']-item['change']))
    print("Strike Price before news: "+ strikePrice)
    print("Max Expiration Date: "+ expirationDate)
    print(f"Option code: {get_option_code(symbol, 'C', float(strikePrice), expirationDate)}")