# utils/tradeSignalAlgorithm.py
import sys, json, time, random, os
from filelock import FileLock

def main():
    if len(sys.argv) < 2:
        print("Usage: python tradeSignalAlgorithm.py <listing_url>")
        return

    listing_url = sys.argv[1]
    unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"

    new_entry = {
        "id": unique_id,
        "listing_url": listing_url
    }

    filename = "trade_signals.json"
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

        data.append(new_entry)

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    print(f"Added trade signal: {new_entry}")

if __name__ == "__main__":
    main()
