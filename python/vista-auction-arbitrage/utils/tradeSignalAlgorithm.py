# utils/tradeSignalAlgorithm.py
import sys, json, time, random, os
from filelock import FileLock

def create_trade_signal(listing_url):
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python tradeSignalAlgorithm.py <listing_url>")
        return
    listing_url = sys.argv[1]
    # Generate trade signal from listing URL
    trade_signal = create_trade_signal(listing_url)
    write_json_atomic("trade_signals.json", trade_signal)
    print(f"Generated trade signal: {trade_signal}")

if __name__ == "__main__":
    main()
