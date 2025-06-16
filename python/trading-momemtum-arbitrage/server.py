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

def is_options_available(ticker_symbol):
    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker_symbol}?feed={FEED}&limit=1"
    response = requests.get(url, headers=headers)
    return response.status_code == 200 and response.json()['snapshots'] != {}

def get_nearest_friday():
    today = date.today()
    weekday = today.weekday()
    
    days_until_friday = (4 - weekday) % 7
    
    nearest_friday = today + timedelta(days=days_until_friday)
    
    return nearest_friday.strftime("%y%m%d")

def getOptionCode(symbol, expirationDate, strikePrice, optionType='C'):
    return f"{symbol.upper()}{expirationDate}{optionType}00{str(float(strikePrice)*10).replace(".","")}0"

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
    symbol = item['symbol']
    expirationDate = get_nearest_friday()
    strikePrice = str(math.floor((item['price']-item['change'])*2)/2)
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Strike Price before news: "+ strikePrice)
    print("Max Expiration Date: "+ expirationDate)
    print(f"Option code: {getOptionCode(symbol, expirationDate, strikePrice)}")
print("\nTop Losers:")
for item in losers:
    symbol = item['symbol']
    expirationDate = get_nearest_friday()
    strikePrice = str(math.ceil((item['price']-item['change'])*2)/2)
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Price before news: "+ str(item['price']-item['change']))
    print("Strike Price before news: "+ strikePrice)
    print("Max Expiration Date: "+ expirationDate)
    print(f"Option code: {getOptionCode(symbol, expirationDate, strikePrice)}")