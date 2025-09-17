# utils/tradeSignalAlgorithm.py
import sys, json, time, random, os, subprocess
from filelock import FileLock

def run_gemini_prompt(command: str, model: str = "gemini-2.5-flash"):
    """
    Runs a gemini cli prompt and returns (stdout, stderr, returncode)
    """
    try:
        result = subprocess.run(
            ["gemini", "--model", model, "--prompt", command],
            shell=True,
            capture_output=True,
            text=True
        )
        # Get the standard output and split it by newlines
        stdout_lines = result.stdout.strip().split('\n')

        # The URL is the last line of the output
        if stdout_lines:
            url_output = stdout_lines[-1].strip()
            # Basic validation to ensure it looks like a URL
            if url_output.startswith("http"):
                return url_output, result.stderr, result.returncode

        # If the URL is not found, return empty string with the original stderr and returncode
        return "", result.stderr, result.returncode
    except Exception as e:
        raise RuntimeError(f"Error running command: {e}")

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

def main():
    if len(sys.argv) < 2:
        print("Usage: python tradeSignalAlgorithm.py <listing_url>")
        return
    listing_url = sys.argv[1]
    # Generate trade signal from listing URL
    trade_signal = create_trade_signal(listing_url)
    write_json_atomic("trade_signals.json", trade_signal)
    print(f"Generated trade signal: {trade_signal}")
    stdout, stderr, code = run_gemini_prompt("This link "+listing_url+" is for an item on auction. This listing might have a URL to amazon for this product. If it does, show me only that link and nothing else. If it does not, return the string 'Not Found'")
    print("Gemini Output:", stdout)

if __name__ == "__main__":
    main()
