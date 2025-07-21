import os
import requests
import json
from dotenv import load_dotenv

# LOAD ENVIRONMENT VARIABLES once when the module is imported
load_dotenv()
ALPACA_ACCOUNT_URL = os.getenv('ALPACA_ACCOUNT_URL', 'https://paper-api.alpaca.markets/v2')
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
ALPACA_FEED = os.getenv('ALPACA_FEED', 'indicative')
if not all([ALPACA_ACCOUNT_URL, ALPACA_KEY, ALPACA_SECRET, ALPACA_FEED]):
    raise EnvironmentError("One or more Alpaca API environment variables are not set.")

def create_credit_spread_order(buy_symbol: str, sell_symbol: str, quantity: int, limit_price: float, time_in_force: str = 'day') -> dict:
    """
    Places a multileg order with Alpaca for options trading.

    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET
    }

    payload = {
        "type": "limit",
        "time_in_force": time_in_force,
        "order_class": "mleg",
        "limit_price": limit_price,
        "qty": str(quantity),  # Quantity needs to be a string
        "legs": [
            {
                "symbol": sell_symbol,
                "ratio_qty": "1",
                "side": "sell", # buy or sell
                "position_intent": "sell_to_open",
            },
            {
                "symbol": buy_symbol,
                "ratio_qty": "1",
                "side": "buy", # buy or sell
                "position_intent": "buy_to_open",
            }
        ]
    }

    try:
        # Construct the full URL for the orders endpoint
        full_url = f"{ALPACA_ACCOUNT_URL}/orders"

        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response status code: {response.status_code}")
        try:
            error_details = response.json()
            print(f"Alpaca Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": "HTTP Error", "details": error_details, "status_code": response.status_code}
        except json.JSONDecodeError:
            print(f"Alpaca Error Details: {response.text}")
            return {"error": "HTTP Error", "details": response.text, "status_code": response.status_code}

def create_order(
    trade_symbol: str,
    quantity: int,
    side: str,  # "buy" or "sell"
    limit_price: float,
    order_type: str = "limit",  # Default to "limit"
    time_in_force: str = "day"  # Default to "day"
) -> dict:
    """
    Places an stock or option order with Alpaca.

    Args:
        trade_symbol (str): The symbol of the option contract (e.g., "SPY250630C00345000").
        quantity (int): The number of option contracts to trade.
        side (str): The side of the order ("buy" or "sell").
        limit_price (float): The limit price (premium) for the option order.
        order_type (str, optional): The type of order ("market", "limit", "stop", etc.). Defaults to "limit".
        time_in_force (str, optional): The time-in-force for the order ("day", "gtc", etc.). Defaults to "day".

    Returns:
        dict: A dictionary containing the JSON response from Alpaca API if successful.
              Returns an error dictionary if the request fails.
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET
    }

    payload = {
        "symbol": trade_symbol,
        "qty": str(quantity),  # Quantity needs to be a string
        "side": side,
        "type": order_type,
        "time_in_force": time_in_force,
        "extended_hours": True if (order_type == 'limit' and time_in_force == 'day') else False,
    }

    if order_type == "limit":
        payload["limit_price"] = str(limit_price) # Limit price needs to be a string

    try:
        # Construct the full URL for the orders endpoint
        full_url = f"{ALPACA_ACCOUNT_URL}/orders"

        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response status code: {response.status_code}")
        try:
            error_details = response.json()
            print(f"Alpaca Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": "HTTP Error", "details": error_details, "status_code": response.status_code}
        except json.JSONDecodeError:
            print(f"Alpaca Error Details: {response.text}")
            return {"error": "HTTP Error", "details": response.text, "status_code": response.status_code}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return {"error": "Connection Error", "details": str(conn_err)}
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return {"error": "Timeout Error", "details": str(timeout_err)}
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        return {"error": "Unexpected Request Error", "details": str(req_err)}
    except Exception as e:
        print(f"An unhandled error occurred: {e}")
        return {"error": "Unhandled Error", "details": str(e)}

# --- Example Usage ---
# print("--- Attempting to place a BUY order ---")
# order_result = create_order(
#     trade_symbol="SPY250630C00345000",
#     quantity=1,
#     side="buy",
#     limit_price=0.01
# )
# print("\nOrder Result:")
# print(json.dumps(order_result, indent=2))