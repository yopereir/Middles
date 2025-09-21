# Usage python utils/getEbayListings.py "iphone 14"
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from datetime import datetime, timedelta
import re

def scrape_ebay_sold_first_two_pages(product_name: str):
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    listings = []

    for page in range(1, 3):  # pages 1 and 2
        url = f"https://www.ebay.com/sch/i.html?_nkw={product_name}&LH_Complete=1&LH_Sold=1&_sop=10&_pgn={page}"
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.s-card")))

        # Scroll to bottom to load lazy items
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        items = driver.find_elements(By.CSS_SELECTOR, "li.s-card")
        for item in items:
            try:
                link_elem = item.find_element(By.CSS_SELECTOR, "a.su-link")
                title_elem = item.find_element(By.CSS_SELECTOR, "div.s-card__title > span")
                price_elem = item.find_element(By.CSS_SELECTOR, "span.s-card__price")
                try:
                    date_elem = item.find_element(By.CSS_SELECTOR, "div.s-card__caption > span")
                    date_text = date_elem.text.strip()
                except:
                    date_text = ""

                listings.append({
                    "title": title_elem.text.strip(),
                    "price": price_elem.text.strip(),
                    "date": date_text,
                    "link": link_elem.get_attribute("href")
                })
            except:
                continue

    driver.quit()
    return listings  # return as list of dicts


# ---------------- Robust filter for last 60 days with average and lowest price ----------------
def filter_recent_listings(product_name = "", days=60):
    recent_listings = []
    now = datetime.now()
    numeric_prices = []
    listings = scrape_ebay_sold_first_two_pages(product_name)

    for item in listings:
        date_text = item.get("date", "").strip()
        # Remove "Sold" or "Completed"
        date_text = re.sub(r"^(Sold|Completed)\s*", "", date_text, flags=re.I)
        if not date_text:
            continue

        # Parse date
        try:
            sold_date = datetime.strptime(date_text, "%b %d, %Y")
        except:
            continue

        # Keep only items within last `days`
        if now - sold_date <= timedelta(days=days):
            # Convert price to numeric
            price_text = item.get("price", "")
            match = re.search(r"[\d,.]+", price_text)
            if match:
                price_val = float(match.group(0).replace(",", ""))
                item["price"] = price_val  # replace string with numeric
                numeric_prices.append(price_val)
            else:
                continue  # skip if price cannot be parsed

            recent_listings.append(item)

    total_count = len(recent_listings)
    lowest_price = min(numeric_prices) if numeric_prices else None
    average_price = round(sum(numeric_prices) / total_count, 2) if total_count > 0 else None

    return {
        "total_count": total_count,
        "lowest_price": lowest_price,
        "average_price": average_price,
        #"listings": recent_listings
    }


# ---------------- Command-line interface ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape eBay sold listings for a product (first 2 pages) and filter by last 60 days.")
    parser.add_argument("product", type=str, help="Product name to search on eBay")
    args = parser.parse_args()

    product_name = args.product
    result = filter_recent_listings(product_name, days=60)

    print(json.dumps(result, indent=2))
