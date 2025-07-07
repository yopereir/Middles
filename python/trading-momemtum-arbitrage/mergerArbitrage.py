import asyncio, websockets, math, os, json
from dotenv import load_dotenv
from utils.getAIResponse import query_gemini, extract_json_from_text
from utils.getAccountDetails import getAccountBalance
from utils.getStockDetails import getAskingPrice

load_dotenv()
ALPACA_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET = os.getenv('ALPACA_API_SECRET')
# The correct WebSocket URL for news data is wss://stream.data.alpaca.markets/v1beta1/news
# For paper trading news, it would be wss://stream.data.sandbox.alpaca.markets/v1beta1/news
WEBSOCKET_NEWS_URL = os.getenv("ALPACA_WEBSOCKET_NEWS_URL", "wss://stream.data.alpaca.markets/v1beta1/news")
promptResponseDefinition = "Read the following news and generate a trade signal and nothing else. Trade signal should be a json object having only the following keys: Direction, Ticker, buyPrice, sellPrice. The Direction should be 'buy' if it is positive news for the company being acquired or 'sell' if it is negative news. The ticker symbol is only for the symbol of the company being acquired. All values in the JSON will be a string. If you are less than 50 percent confident about a value or there is no information available, enter 'unsure' as the string. Your output should only be in json format. The trade signal is only for merger and acquisition news so if you are not confident that the news can be categorized as such, set all values to `unsure` in the json response. News: "
principal_balance=getAccountBalance()
max_investment_unit=float(principal_balance)*0.05

async def listen_to_news():
    async with websockets.connect(WEBSOCKET_NEWS_URL) as websocket:
        print(f"Connected to Alpaca News WebSocket at {WEBSOCKET_NEWS_URL}")

        # 1. Authenticate
        auth_message = {
            "action": "auth",
            "key": ALPACA_KEY,
            "secret": ALPACA_SECRET
        }
        await websocket.send(json.dumps(auth_message))
        auth_response = await websocket.recv()
        print(f"Authentication Response: {auth_response}")
        
        # Check if authentication was successful
        auth_status = json.loads(auth_response)[0].get("T")
        if auth_status != "success":
            print(f"Authentication failed: {auth_response}")
            return # Exit if authentication fails

        # 2. Subscribe to news
        # To subscribe to all news, use "*"
        # To subscribe to specific symbols, use ["AAPL", "MSFT"] etc.
        subscribe_message = {
            "action": "subscribe",
            "news": ["*"] 
        }
        await websocket.send(json.dumps(subscribe_message))
        subscribe_response = await websocket.recv()
        print(f"Subscription Response: {subscribe_response}")

        try:
            while True:
                message = await websocket.recv()
                # Alpaca sends messages as JSON arrays.
                # Each element in the array is a news event/article.
                events = json.loads(message)
                for event in events:
                    # News events have a "T" field of "n"
                    if event.get("T") == "n":
                        print(f"--- NEWS ARTICLE ---")
                        print(f"ID: {event.get('id')}")
                        print(f"Headline: {event.get('headline')}")
                        print(f"Summary: {event.get('summary')}")
                        print(f"Symbols: {event.get('symbols')}")
                        print(f"Created At: {event.get('created_at')}")
                        print(f"URL: {event.get('url')}")
                        print(f"--------------------")
                        trade_signal = extract_json_from_text(query_gemini(promptResponseDefinition+"\nHeadline: "+event['headline']+"\nURL: "+event['url']))
                        print(trade_signal)
                        if trade_signal['Ticker'] == 'unsure' or trade_signal['Direction'] == 'unsure':
                            print("Skipping order creation due to None in ticker or direction.")
                            continue
                        sharesToBuy = math.floor((max_investment_unit if (max_investment_unit < float(getAccountBalance())) else getAccountBalance())/getAskingPrice(trade_signal['Ticker']))
                        print(sharesToBuy)
                    else:
                        print(f"Received non-news message: {event}")
        except websockets.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(listen_to_news())