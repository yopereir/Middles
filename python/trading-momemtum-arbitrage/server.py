import os, requests, math
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from py_vollib.black_scholes.implied_volatility import implied_volatility as bsiv

# LOAD ENVIRONMENT VARIABLES
load_dotenv()
ALPACA_URL = os.getenv('ALPACA_ACCOUNT_URL')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
FEED = os.getenv('ALPACA_FEED', 'indicative')
LIMIT = os.getenv('ALPACA_LIMIT', '10')
RISK_FREE_RATE = float(os.getenv('RISK_FREE_RATE', '0.05'))

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

def get_option_premium(options_symbol):
    url = f"https://data.alpaca.markets/v1beta1/options/quotes/latest?symbols={options_symbol}&feed={FEED}"
    response = requests.get(url, headers=headers)
    optionQuoteDetails = response.json()['quotes'][options_symbol]
    return abs(optionQuoteDetails['bp'] + optionQuoteDetails['ap'])/2 # Return average of bid and ask prices

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
    currentStockPrice = item['price']
    strikePrice = str(math.floor((item['price']-item['change'])*2)/2)
    timeToExpiration = 1/365 * abs((datetime.strptime(expirationDate, "%Y-%m-%d").date() - date.today()).days)
    call_or_put = 'P'
    optionPremium = get_option_premium(get_option_code(symbol, call_or_put, float(strikePrice), expirationDate))
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Strike Price before news: "+ strikePrice)
    print("Max Expiration Date: "+ expirationDate)
    print(f"Option code: {get_option_code(symbol, call_or_put, float(strikePrice), expirationDate)}")
    print("Implied volatility: ",bsiv(optionPremium, currentStockPrice, float(strikePrice), timeToExpiration, RISK_FREE_RATE, call_or_put.lower()))

print("\nTop Losers:")
for item in losers:
    symbol = item['symbol']
    expirationDate = get_nearest_friday()
    currentStockPrice = item['price']
    strikePrice = str(math.ceil((item['price']-item['change'])*2)/2)
    timeToExpiration = 1/365 * abs((datetime.strptime(expirationDate, "%Y-%m-%d").date() - date.today()).days)
    call_or_put = 'C'
    optionPremium = get_option_premium(get_option_code(symbol, call_or_put, float(strikePrice), expirationDate))
    print(f"{item['symbol']}: {item['percent_change']}%")
    print("Price before news: "+ str(item['price']-item['change']))
    print("Strike Price before news: "+ strikePrice)
    print("Max Expiration Date: "+ expirationDate)
    print(f"Option code: {get_option_code(symbol, call_or_put, float(strikePrice), expirationDate)}")
    print("Parameters for implied volatility calculation:")
    print(f"Current Stock Price: {currentStockPrice}, Strike Price: {strikePrice}, Time to Expiration: {timeToExpiration}, Risk-Free Rate: {RISK_FREE_RATE}, Option Premium: {optionPremium}, Call or Put: {call_or_put.lower()}")
    print("Implied volatility (1=100%): ",bsiv(optionPremium, currentStockPrice, float(strikePrice), timeToExpiration, RISK_FREE_RATE, call_or_put.lower()))