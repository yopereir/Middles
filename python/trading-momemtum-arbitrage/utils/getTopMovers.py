import os
import requests
from dotenv import load_dotenv
from getOptionDetails import calculate_option_details

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

def calculate_sharpe_ratio(expected_return: float, risk_free_rate: float, volatility: float) -> float | None:
    """
    Calculates the Sharpe Ratio.

    Args:
        expected_return (float): The expected return of the investment.
        risk_free_rate (float): The risk-free rate of return.
        volatility (float): The standard deviation (or implied volatility in this context) of the investment.

    Returns:
        float or None: The calculated Sharpe Ratio, or None if volatility is zero.
    """
    if volatility == 0:
        return None # Avoid division by zero
    
    excess_return = expected_return - risk_free_rate
    sharpe = excess_return / volatility
    return sharpe

def get_top_movers(limit: int):
    """
    Fetches top stock gainers and losers from Alpaca and enriches them
    with relevant options data (strike, premium, implied volatility).

    Returns:
        tuple: A tuple containing two lists: (gainers, losers).
               Each list contains dictionaries with stock and calculated option details.
    """
    url = f"{ALPACA_DATA_BETA_URL}/screener/stocks/movers?top={limit}"
    print(url)
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching stock movers: {response.status_code} - {response.text}")
        return [], [] # Return empty lists on error

    response_data = response.json()
    
    raw_gainers = response_data.get('gainers', [])
    raw_losers = response_data.get('losers', [])

    processed_gainers = []
    processed_losers = []

    print("\nProcessing Top Gainers (looking for Put options)...")
    for item in raw_gainers:
        # Gainers: look for Puts
        processed_item = calculate_option_details(item, 'P')
        if processed_item:
            processed_gainers.append(processed_item)

    print("\nProcessing Top Losers (looking for Call options)...")
    for item in raw_losers:
        # Losers: look for Calls
        processed_item = calculate_option_details(item, 'C')
        if processed_item:
            processed_losers.append(processed_item)

    # Sort the processed lists by percent_change
    processed_gainers.sort(key=lambda x: x['percent_change'], reverse=True)
    processed_losers.sort(key=lambda x: x['percent_change'], reverse=False) # Losers: most negative first

    if not processed_gainers and not processed_losers:
        print("No valid gainers or losers data found after processing options.")

    return processed_gainers, processed_losers

# Example of how to use this module
# gainers, losers = get_top_movers()
# print("\n--- Processed Top Gainers (with Put Option Info and Sharpe Ratio) ---")
# if gainers:
#     for item in gainers:
#         print(f"Symbol: {item['symbol']} ({item['percent_change']}%)")
#         print(f"  Current Stock Price: {item['price']}")
#         print(f"  Strike Price (P): {item['strike_price_float']}")
#         print(f"  Expiration Date: {item['expiration_date']}")
#         print(f"  Option Code (Put): {item['option_symbol']}")
#         print(f"  Option Premium: {item['option_premium']:.2f}")
#         if item['implied_volatility'] is not None:
#             print(f"  Implied Volatility: {item['implied_volatility']:.4f} ({(item['implied_volatility']*100):.2f}%)")
#         else:
#             print("  Implied Volatility: N/A")

#         print("-" * 30)
# else:
#     print("No gainers found with valid put options.")

# print("\n--- Processed Top Losers (with Call Option Info and Sharpe Ratio) ---")
# if losers:
#     for item in losers:
#         print(f"Symbol: {item['symbol']} ({item['percent_change']:.2f}%)")
#         print(f"  Current Stock Price: {item['price']}")
#         print(f"  Strike Price (C): {item['strike_price_float']}")
#         print(f"  Expiration Date: {item['expiration_date']}")
#         print(f"  Option Code (Call): {item['option_symbol']}")
#         print(f"  Option Premium: {item['option_premium']:.2f}")
#         if item['implied_volatility'] is not None:
#             print(f"  Implied Volatility: {item['implied_volatility']:.4f} ({(item['implied_volatility']*100):.2f}%)")
#         else:
#             print("  Implied Volatility: N/A")
#         print("-" * 30)
# else:
#     print("No losers found with valid call options.")
