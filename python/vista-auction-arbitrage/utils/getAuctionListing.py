import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re

def scrape_vistaauction_listing(url: str):
    # ---------------- Chrome options ----------------
    options = Options()
    options.headless = True  # set False to debug
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # ---------------- Get item name ----------------
    try:
        title_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.detail__title"))
        )
        item_name = title_elem.text.strip()
    except:
        item_name = None

    # ---------------- Get MSRP and Condition ----------------
    try:
        subtitle_elem = driver.find_element(By.CSS_SELECTOR, "h4.detail__subtitle")
        subtitle_text = subtitle_elem.text.strip()  # e.g., "MSRP: $399.99  - New"
        msrp_match = re.search(r"MSRP:\s*\$([\d,.]+)", subtitle_text)
        condition_match = re.search(r"-\s*(\w+)$", subtitle_text)
        msrp = float(msrp_match.group(1).replace(",", "")) if msrp_match else None
        condition = condition_match.group(1) if condition_match else None
    except:
        msrp = None
        condition = None

    # ---------------- Get Quick Bid ----------------
    try:
        quick_bid_elem = driver.find_element(By.CSS_SELECTOR, "a#PlaceQuickBid span.NumberPart")
        quick_bid = float(quick_bid_elem.text.strip().replace(",", ""))
    except:
        quick_bid = None

    driver.quit()

    return json.dumps({
        "name": item_name,
        "msrp": msrp,
        "condition": condition,
        "quick_bid": quick_bid
    }, indent=2)


# ---------------- Command-line interface ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Vista Auction listing info")
    parser.add_argument("url", type=str, help="URL of the Vista Auction listing")
    args = parser.parse_args()

    result = scrape_vistaauction_listing(args.url)
    print(result)
