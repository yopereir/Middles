# Use case: python tradeSignalAlgorithm.py --keywords bathroom --negative_keywords shirt,jacket,coat,pant,jean,shorts,sneaker,shoe,glove,mittens,scarf
import json, time, random, os, argparse
from filelock import FileLock
from utils.getAuctionListings import fetch_auction_listings
from utils.getAuctionListing import scrape_vistaauction_listing
from utils.getEbayListings import filter_recent_listings

def create_trade_signal(listing_url): # Default returns {}
    unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
    trade_signal = {
        "id": unique_id,
        "listing_url": listing_url
    }
    return trade_signal


def write_json_atomic(filename = "trade_signals.json", trade_signal = {}):
    lockfile = filename + ".lock"
    lock = FileLock(lockfile)

    with lock:  # prevent concurrent write corruption
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
            except json.JSONDecodeError:
                data = []
        else:
            data = []
        data.append(trade_signal)
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

def custom_filter(item):
    vista_auction_fee = 2
    vista_auction_commission = 0.10  # 10%
    shipping_fee = 20
    ebay_commission = 0.15  # 15%
    profit_margin = 0.20  # 20%
    profit = 0
    if item.get("average_price") and item.get("quick_bid"):
        max_bid = item["quick_bid"] * (1 + profit_margin + vista_auction_commission + ebay_commission) \
                  + vista_auction_fee + shipping_fee + profit
        if item["average_price"] > max_bid:
            # Add max_bid field to the item
            item["max_bid"] = max_bid
            return True
    return False

def broadcast_trade_signal(listing_url):
    trade_signal = create_trade_signal(listing_url)
    write_json_atomic("trade_signals.json", trade_signal)

if __name__ == "__main__":
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, default="", help="Comma-separated keywords")
    parser.add_argument("--negative_keywords", type=str, default="", help="Comma-separated negative keywords")
    args = parser.parse_args()
    keywords = args.keywords.split(",") if args.keywords else []
    negative_keywords = args.negative_keywords.split(",") if args.negative_keywords else []

    # Fetch auction listings with keyword, time range and ratio filters
    results = fetch_auction_listings(keywords=keywords, negative_keywords=negative_keywords)

    # Get details of each listing
    for item in results:
        link = item.get("link")
        if link:
            item.update(scrape_vistaauction_listing(link))

    # Get Ebay details of each listing
    for item in results:
        name = item.get("name")
        if name:
            item.update(filter_recent_listings(name))

    # Add your own logic here to decide which listings to broadcast
    results = [item for item in results if custom_filter(item)]

    # Broadcast trade signals for each listing
    print(json.dumps(results, indent=2))
    for item in results:
        link = item.get("link")
        if link:
            print(f"Broadcasting trade signal for: {link}")
            broadcast_trade_signal(link)
