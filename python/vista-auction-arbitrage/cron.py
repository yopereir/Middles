# Usage: python cron.py --interval 180 --total_spent_file total_spent.txt --spending_limit 500 --script tradeSignalAlgorithm.py -- --keywords bathroom,mower --negative_keywords shirt,jacket,coat,pant,jean,dress --max_seconds 300 --min_seconds 180 --max_ratio 0.2 --max_pages 10
import subprocess
import time
import argparse
import sys
import os

parser = argparse.ArgumentParser(description="Call another Python script at intervals")
parser.add_argument("--interval", type=int, default=60, help="Interval in seconds between calls")
parser.add_argument("--total_spent_file", type=str, required=True, help="File to track total amount spent")
parser.add_argument("--spending_limit", type=float, required=True, help="Stop cron if total spent exceeds this value")
parser.add_argument("--script", type=str, required=True, help="Path to the Python script to call")
parser.add_argument("script_args", nargs=argparse.REMAINDER, help="Arguments to pass to the called script")
args = parser.parse_args()

interval = args.interval
total_spent_file = args.total_spent_file
spending_limit = args.spending_limit
script_path = args.script
script_args = args.script_args
if script_args and script_args[0] == "--":
    script_args = script_args[1:]  # strip the first element

print(f"Starting loop: calling {script_path} every {interval} seconds...")

while True:
    # Check total spent before running the script
    total_spent = 0.0
    if os.path.exists(total_spent_file):
        try:
            with open(total_spent_file, "r") as f:
                content = f.read().strip()
                if content:
                    total_spent = float(content)
        except ValueError:
            print(f"Warning: {total_spent_file} contains invalid number, treating as 0.0")
    
    if total_spent > spending_limit:
        print(f"Total spent {total_spent} exceeds limit {spending_limit}. Stopping cronjob.")
        sys.exit(0)

    try:
        # Call the second script with any additional arguments
        subprocess.run(["python", script_path, *script_args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while calling {script_path}: {e}")
    
    # Wait for the interval
    time.sleep(interval)
