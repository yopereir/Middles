import time, math, json
from utils.createTrade import create_order
from utils.getSnPFeed import fetch_press_releases
from utils.getAIResponse import query_gemini, extract_json_from_text
from utils.getAccountDetails import getAccountBalance, getAccountKey
from utils.getStockDetails import getAskingPrice, getBidPrice, getLastTradePrice
from utils.getSnPTradeSignals import get_snp_trade_signals

POLL_INTERVAL = 61
latest_processessed_press_release_id = None
latest_press_release = {}
principal_balance=getAccountBalance()
max_investment_unit=float(principal_balance)*0.05

def execute_trade_signal(trade_signal):
    """
    Executes the trade signal by creating an order.
    """
    print(trade_signal)
    if trade_signal['Ticker'] is None or trade_signal['Direction'] is None:
        print("Skipping order creation due to None in ticker or direction.")
        raise ValueError("Invalid trade signal: Ticker or Direction is None")
    # Create Alpaca trade
    if trade_signal['Direction'] == 'buy':
        sharesToBuy = math.floor((max_investment_unit if (max_investment_unit < float(getAccountBalance())) else getAccountBalance())/(getAskingPrice(trade_signal['Ticker']) if getAskingPrice(trade_signal['Ticker']) > 0 else getLastTradePrice(trade_signal['Ticker'])))
        print("Shares to buy: " + str(sharesToBuy))
        limitPrice = round(float(getLastTradePrice(trade_signal['Ticker']))*1.01, 2)
        print("Limit Price: " + str(limitPrice))
        create_order(trade_signal['Ticker'], sharesToBuy, trade_signal['Direction'], limitPrice, 'limit', 'day')
    elif trade_signal['Direction'] == 'sell':
        sharesToSell = math.floor((max_investment_unit if (max_investment_unit < float(getAccountBalance())) else getAccountBalance())/(getBidPrice(trade_signal['Ticker']) if getBidPrice(trade_signal['Ticker']) > 0 else getLastTradePrice(trade_signal['Ticker'])))
        limitPrice = round(float(getLastTradePrice(trade_signal['Ticker']))*0.99, 2)
        print("Shares to sell: " + str(sharesToSell))
        print("Limit Price: " + str(limitPrice))
        create_order(trade_signal['Ticker'], sharesToSell, trade_signal['Direction'], limitPrice, 'limit', 'day')

def main():
    global latest_processessed_press_release_id
    print(f"Using Account Key: {getAccountKey()}")
    while True:
        try:
            # Fetch news articles
            latest_press_release = fetch_press_releases()
            # Run only if new news article
            if latest_press_release.get("id") != latest_processessed_press_release_id:
                latest_processessed_press_release_id = latest_press_release.get("id")
                # S&P Addition Trade Signal
                trade_signals = []
                # INFO: use this if you want to use AI to create trade signal.
                # trade_signals.append(extract_json_from_text(query_gemini("Generate a trade signal for the stock market for ONLY stocks that are joining the S&P 500 index. The signal is a json object having 2 parameters- Ticker, Direction. Ticker is the stock symbol and Direction is either buy or sell. If you are not sure about the ticker symbol or the direction, set both values to null. Generate only the trade signal json object and nothing else for this article: "+latest_press_release['url'])))
                # ------------------------------------ #
                # INFO: use below if you want to get trade signal via web scraping
                trade_signals = json.loads(get_snp_trade_signals(latest_press_release['url']))
                print(f"Trade Signals: {trade_signals}")
                for trade_signal in trade_signals:
                    trade_signal['Direction'] = 'buy' if trade_signal['Action'] == 'Addition' else 'sell' if trade_signal['Action'] == 'Deletion' else None
                # ------------------------------------ #
                for trade_signals in trade_signals:
                    execute_trade_signal(trade_signals)
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
