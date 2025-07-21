import requests
import time

API_URL = "https://sandpglobal-spglobal-live.cphostaccess.com/en/press/press-releases/pr-newswire-content.aspx?page-nbr=0"
POLL_INTERVAL = 300  # check every 5 minutes
latest_seen_id = None  # initially None
latest_press_release = {}

def handle_news_item(title, link, date):
    print(f"\n📰 {date} — {title}\n🔗 {link}\n{'-'*80}")

def fetch_press_releases():
    global latest_seen_id

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://sandpglobal-spglobal-live.cphostaccess.com/en/press/press-release",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    data = response.json()

    items = data.get("itemsList", [])
    new_items = []

    for item in items:
        item_id = item.get("id")
        if not item_id:
            continue
        if item_id == latest_seen_id:
            break  # stop once we reach the last seen item

        new_items.append(item)

    # Process in chronological order (oldest first)
    for item in reversed(new_items):
        title = item.get("headline", "").strip()
        link = item.get("url", "").strip()
        date = item.get("releaseDate", "").strip()
        handle_news_item(title, link, date)

    # Update latest_seen_id
    if items:
        latest_seen_id = items[0].get("id")
        return items[1]

# Example to call from other functions
def main():
    while True:
        try:
            latest_press_release = fetch_press_releases()
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
