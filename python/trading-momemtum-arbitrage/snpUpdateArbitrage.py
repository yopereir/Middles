import time
from utils.createTrade import create_order
from utils.getSnPFeed import fetch_press_releases
from utils.getAIResponse import query_gemini, extract_json_from_text

POLL_INTERVAL = 11
latest_processessed_press_release_id = None
latest_press_release = {}

def main():
    global latest_processessed_press_release_id
    while True:
        try:
            # Fetch news articles
            latest_press_release = fetch_press_releases()
            # Run only if new news article
            if latest_press_release.get("id") != latest_processessed_press_release_id:
                latest_processessed_press_release_id = latest_press_release.get("id")
                # Get trade signal
                trade_signal = extract_json_from_text(query_gemini("Generate a trade signal for the stock market. The signal is a jsob object having 2 parameters- Ticker, Direction. Ticker is the stock symbol and Direction is either buy or sell. If you are not about the ticker symbol or the direction, set both values to null. Generate only the trade signal json object and nothing else for this article: "+latest_press_release['url']))
                print(trade_signal)
                # Create Alpaca trade
                create_order(trade_signal['Ticker'], 10, trade_signal['Direction'], 0, 'market', 'gtc')
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()