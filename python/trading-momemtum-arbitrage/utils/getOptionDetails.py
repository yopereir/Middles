import os
import requests
import math
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from py_vollib.black_scholes.implied_volatility import implied_volatility as bsiv

# LOAD ENVIRONMENT VARIABLES
load_dotenv()
ALPACA_DATA_URL = os.getenv('ALPACA_DATA_URL','https://data.alpaca.markets/v2')
ALPACA_DATA_BETA_URL = os.getenv('ALPACA_DATA_BETA_URL','https://data.alpaca.markets/v1beta1')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
FEED = os.getenv('ALPACA_FEED', 'indicative')
RISK_FREE_RATE = float(os.getenv('RISK_FREE_RATE', '0.05'))

# Ensure essential environment variables are loaded
if not all([ALPACA_DATA_URL, ALPACA_DATA_BETA_URL, ALPACA_KEY, ALPACA_SECRET]):
    raise EnvironmentError("One or more Alpaca API environment variables are not set (ALPACA_DATA_URL, ALPACA_DATA_BETA_URL, ALPACA_API_KEY, ALPACA_API_SECRET).")

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET
}

def get_nearest_friday():
    today = date.today()
    weekday = today.weekday()
    # If today is Friday, it will return today. Otherwise, it will return the next Friday.
    # For options, typically the next *standard* expiration is used, which is often a Friday.
    days_until_friday = (4 - weekday + 7) % 7 # ensures it's always Friday or next Friday
    if days_until_friday == 0: # If today is Friday, ensure it's still today's date
        nearest_friday = today
    else:
        nearest_friday = today + timedelta(days=days_until_friday)
    return nearest_friday.strftime("%Y-%m-%d")

def get_option_code(symbol: str, call_or_put: str, strike_price: float, expiration_date: str):
    """
    Generates an Alpaca-compatible options symbol.

    Args:
        symbol (str): The underlying stock symbol (e.g., 'AAPL').
        call_or_put (str): 'C' for Call, 'P' for Put.
        strike_price (float): The strike price of the option.
        expiration_date (str): The expiration date in 'YYYY-MM-DD' format.

    Returns:
        str: The formatted options symbol.
    """
    root = symbol.upper()
    date_part = expiration_date.replace('-', '')[2:]  # get YYMMDD
    cp = call_or_put.upper()
    # Convert to integer with 3 decimal precision and pad to 8 digits
    strike_part = f"{int(round(strike_price * 1000)):08d}"
    return f"{root}{date_part}{cp}{strike_part}"

def get_option_premium(options_symbol: str) -> float:
    """
    Fetches the latest bid/ask premium for an option and returns their average.

    Args:
        options_symbol (str): The Alpaca options symbol.

    Returns:
        float: The average of bid and ask prices, or 0.0 if not found.
    """
    url = f"{ALPACA_DATA_BETA_URL}/options/quotes/latest?symbols={options_symbol}&feed={FEED}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and options_symbol in response.json().get('quotes', {}):
        option_quote_details = response.json()['quotes'][options_symbol]
        bid_price = option_quote_details.get('bp', 0.0) # Bid Price
        ask_price = option_quote_details.get('ap', 0.0) # Ask Price

        # Handle cases where bid or ask might be zero (illiquid or no data)
        if bid_price == 0.0 and ask_price == 0.0:
            return 0.0
        elif bid_price == 0.0:
            return ask_price
        elif ask_price == 0.0:
            return bid_price
        else:
            return (bid_price + ask_price) / 2
    return 0.0 # Return 0.0 if symbol not found or error

def get_option_latest_trade(options_symbol: str) -> str:
    return requests.get(f"{ALPACA_DATA_BETA_URL}/options/trades/latest?symbols={options_symbol}&feed={FEED}", headers=headers).json()['trades'][options_symbol]['p']

def calculate_option_details(item: dict, call_or_put: str, ticker: str, ending_price: str) -> dict or None:
    """
    Calculates and appends option-related details to a stock item.

    Args:
        item (dict): The stock item dictionary from Alpaca movers.
        call_or_put (str): 'C' for Call, 'P' for Put.

    Returns:
        dict or None: The updated item dictionary with option details, or None if
                      the option is not available or data is insufficient.
    """
    if item != {}:
        symbol = item['symbol']
        expiration_date_str = get_nearest_friday()
        current_stock_price = item['price']
        price_change = item['change']
    else:
        symbol = ticker
        expiration_date_str = get_nearest_friday()
        current_stock_price = ending_price
        price_change = 0.0
    # Determine strike price based on gainer/loser context
    if call_or_put == 'P': # For gainers (buying puts)
        # Assuming you want a strike price near the pre-news price for puts on gainers
        strike_price_float = math.floor((current_stock_price - price_change) * 2) / 2
        secondary_strike_price_float = math.floor((current_stock_price - price_change) * 2) / 2 - .5
    else: # For losers (buying calls)
        # Assuming you want a strike price near the pre-news price for calls on losers
        strike_price_float = math.ceil((current_stock_price - price_change) * 2) / 2
        secondary_strike_price_float = math.ceil((current_stock_price - price_change) * 2) / 2 - .5

    # Check for valid strike price (must be positive)
    if strike_price_float <= 0:
        print(f"Warning: Calculated strike price for {symbol} is non-positive ({strike_price_float}). Skipping.")
        return None

    option_symbol = get_option_code(symbol, call_or_put, strike_price_float, expiration_date_str)
    # Check if option exists / snapshot is available
    snapshot_url = f"{ALPACA_DATA_BETA_URL}/options/snapshots?symbols={option_symbol}&feed={FEED}"
    snapshot_response = requests.get(snapshot_url, headers=headers)
    
    if snapshot_response.status_code != 200 or not snapshot_response.json().get('snapshots', {}):
        # print(f"Option snapshot not available for {option_symbol}. Trying secondary strike price.")
        # Try the secondary strike price if the primary one is not available
        option_symbol = get_option_code(symbol, call_or_put, secondary_strike_price_float, expiration_date_str)
        snapshot_url = f"{ALPACA_DATA_BETA_URL}/options/snapshots?symbols={option_symbol}&feed={FEED}"
        snapshot_response = requests.get(snapshot_url, headers=headers)
    if snapshot_response.status_code != 200 or not snapshot_response.json().get('snapshots', {}):
        # print(f"Option snapshot not available for {option_symbol}. Skipping.")
        return None

    option_premium = float(get_option_premium(option_symbol))
    if option_premium <= 0:
        # print(f"Option premium not available or zero for {option_symbol}. Skipping.")
        return None
    time_to_expiration_days = float((datetime.strptime(expiration_date_str, "%Y-%m-%d").date() - date.today()).days)
    if time_to_expiration_days <= 0:
        # If it's today or past, adjust. For implied volatility, T must be > 0.
        # It's safer to skip if time to expiration is 0 or negative as options expire end of day.
        # Or, you could find the *next* nearest Friday if today is Friday and a fresh option is needed.
        # For simplicity here, we'll skip.
        # print(f"Time to expiration for {option_symbol} is zero or negative. Skipping.")
        return None

    time_to_expiration_years = time_to_expiration_days / 365.0

    try:
        implied_volatility = bsiv(
            option_premium,
            current_stock_price,
            strike_price_float,
            time_to_expiration_years,
            RISK_FREE_RATE,
            call_or_put.lower()
        )
    except Exception as e:
        # bsiv can raise errors if inputs are pathological (e.g., price too far from strike)
        print(f"Could not calculate implied volatility for {option_symbol}: {e}. Skipping.")
        implied_volatility = None # Or np.nan if you prefer pandas/numpy
    
    # Create a new dictionary to avoid modifying the original 'item' in place unnecessarily
    # and to ensure all required keys are present
    processed_item = item.copy()
    processed_item['call_or_put'] = call_or_put
    processed_item['expiration_date'] = expiration_date_str
    processed_item['strike_price_float'] = strike_price_float
    processed_item['option_symbol'] = option_symbol
    processed_item['option_premium'] = option_premium
    processed_item['time_to_expiration_days'] = time_to_expiration_days
    processed_item['time_to_expiration_years'] = time_to_expiration_years
    processed_item['implied_volatility'] = implied_volatility

    return processed_item
