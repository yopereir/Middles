# Use case: python tradeSignalAlgorithm.py --keywords bathroom --negative_keywords shirt,jacket,coat,pant,jean,shorts,sneaker,shoe,glove,mittens,scarf
import json, time, random, os, argparse
from filelock import FileLock
from utils.getAuctionListings import fetch_auction_listings
from utils.getAuctionListing import scrape_vistaauction_listing

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


    print(json.dumps(results, indent=2))
    # Broadcast trade signals for each listing
    for item in results:
        link = item.get("link")
        if link:
            print(f"Broadcasting trade signal for: {link}")
            broadcast_trade_signal(link)
