# Use case: python tradeSignalAlgorithm.py --keywords bathroom --negative_keywords shirt,jacket,coat,pant,jean,dress --max_seconds 300 --min_seconds 180 --max_ratio 0.2 --max_pages 10 --total_spent_file total_spent.txt
import json, time, random, os, argparse
from filelock import FileLock
from utils.getAuctionListings import fetch_auction_listings
from utils.getAuctionListing import scrape_vistaauction_listing
from utils.getEbayListings import filter_recent_listings
from utils.callAppScript import send_listing

def track_amount_spent(increment = 1, filename="total_spent.txt"):
    # Check if file exists, create if not create it
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(str(increment))
        print(f"{filename} created with value: {increment}")
    else:
        # Read the current value
        with open(filename, "r") as f:
            content = f.read().strip()
        try:
            if content:
                current_value = float(content)
                new_value = current_value + increment
            else:
                new_value = increment
        except ValueError:
            # Handle case where content is not a valid float
            new_value = increment
        # Save updated value back to the file
        with open(filename, "w") as f:
            f.write(str(new_value))
        print(f"{filename} updated. New value: {new_value}")

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

if __name__ == "__main__":
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, default="", help="Comma-separated keywords")
    parser.add_argument("--negative_keywords", type=str, default="", help="Comma-separated negative keywords")
    parser.add_argument("--max_pages", type=int, default=10, help="Maximum number of pages to fetch")
    parser.add_argument("--min_seconds", type=int, default=180, help="Minimum seconds to wait between requests")
    parser.add_argument("--max_seconds", type=int, default=300, help="Maximum seconds to wait between requests")
    parser.add_argument("--max_ratio", type=float, default=0.2, help="Maximum ending ratio filter")
    parser.add_argument("--total_spent_file", type=str, default="total_spent.txt", help="File name and location to track total amount spent")
    args = parser.parse_args()
    keywords = args.keywords.split(",") if args.keywords else []
    negative_keywords = args.negative_keywords.split(",") if args.negative_keywords else []

    # Fetch auction listings with keyword, time range and ratio filters
    results = fetch_auction_listings(keywords=keywords, negative_keywords=negative_keywords, max_pages=args.max_pages, min_seconds=args.min_seconds, max_seconds=args.max_seconds, max_ratio=args.max_ratio)

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
        max_bid = item.get("max_bid")
        if link and max_bid:
            print(f"Broadcasting trade signal for: {link} with max bid: {max_bid}")
            send_listing(link, max_bid)
            # Track amount spent
            track_amount_spent(increment=max_bid, filename=args.total_spent_file)
