import os, requests, json
from utils.createTrade import create_order
from utils.getTopMovers import get_top_movers


gainers, losers = get_top_movers(50)
print("\n--- Processed Top Gainers (with Put Option Info and Sharpe Ratio) ---")
if gainers:
    for item in gainers:
        print(f"Symbol: {item['symbol']} ({item['percent_change']}%)")
        print(f"  Current Stock Price: {item['price']}")
        print(f"  Strike Price (P): {item['strike_price_float']}")
        print(f"  Expiration Date: {item['expiration_date']}")
        print(f"  Option Code (Put): {item['option_symbol']}")
        print(f"  Option Premium: {item['option_premium']:.2f}")
        if item['implied_volatility'] is not None:
            print(f"  Implied Volatility: {item['implied_volatility']:.4f} ({(item['implied_volatility']*100):.2f}%)")
            print("--- Attempting to place order ---")
            order_result = create_order(
                trade_symbol=f"{item['option_symbol']}",
                quantity=1,
                side="sell",
                limit_price=f"{item['option_premium']:.2f}"
            )
            print("\nOrder Result:")
            print(json.dumps(order_result, indent=2))
        else:
            print("  Implied Volatility: N/A")

        print("-" * 30)
else:
    print("No gainers found with valid put options.")

print("\n--- Processed Top Losers (with Call Option Info and Sharpe Ratio) ---")
if losers:
    for item in losers:
        print(f"Symbol: {item['symbol']} ({item['percent_change']:.2f}%)")
        print(f"  Current Stock Price: {item['price']}")
        print(f"  Strike Price (C): {item['strike_price_float']}")
        print(f"  Expiration Date: {item['expiration_date']}")
        print(f"  Option Code (Call): {item['option_symbol']}")
        print(f"  Option Premium: {item['option_premium']:.2f}")
        if item['implied_volatility'] is not None:
            print(f"  Implied Volatility: {item['implied_volatility']:.4f} ({(item['implied_volatility']*100):.2f}%)")
            print("--- Attempting to place order ---")
            order_result = create_order(
                trade_symbol=f"{item['option_symbol']}",
                quantity=1,
                side="sell",
                limit_price=f"{item['option_premium']:.2f}"
            )
            print("\nOrder Result:")
            print(json.dumps(order_result, indent=2))
        else:
            print("  Implied Volatility: N/A")
        print("-" * 30)
else:
    print("No losers found with valid call options.")
