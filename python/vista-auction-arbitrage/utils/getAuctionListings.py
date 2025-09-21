# Usage: python utils/getAuctionListings.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, re, json, argparse

# ------------------ Helpers ------------------

def get_auction_links():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get("https://vistaauction.com/?ViewFilter=Current")
    time.sleep(3)

    for _ in range(20):
        if "Starts Closing In" in driver.page_source:
            break
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.5)

    try:
        second_section = driver.find_element(By.XPATH, "//div[contains(., 'Starts Closing In')]")
        link_el = second_section.find_element(By.XPATH, ".//a[contains(@href, '/Event/Details/')]")
        return link_el.get_attribute("href")
    except:
        return "https://vistaauction.com/?ViewFilter=Current"
    finally:
        driver.quit()


def extract_auction_section_id(url):
    match = re.search(r"/Event/Details/(\d+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Could not extract auctionSectionID")


def scroll_to_load_all(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def parse_countdown(text):
    if not text:
        return None
    m = re.search(r"(\d+)\s*Minute[s]?,?\s*(\d+)\s*Second[s]?", text, re.IGNORECASE)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m2 = re.search(r"(\d+)\s*Minute[s]?", text, re.IGNORECASE)
    if m2:
        return int(m2.group(1)) * 60
    m3 = re.search(r"(\d+)\s*Second[s]?", text, re.IGNORECASE)
    if m3:
        return int(m3.group(1))
    return None


def parse_msrp(text):
    if not text:
        return None
    txt = " ".join(text.split())
    m = re.search(r"MSRP[:\s]*\$?([\d,]+(?:\.\d+)?)", txt, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except:
            return None
    m2 = re.search(r"\$([\d,]+(?:\.\d+)?)", txt)
    if m2:
        try:
            return float(m2.group(1).replace(",", ""))
        except:
            return None
    m3 = re.search(r"(\d+(?:\.\d{1,2})?)", txt)
    if m3:
        try:
            return float(m3.group(1))
        except:
            return None
    return None


def parse_bid_value(section):
    try:
        candidates = section.find_elements(By.XPATH, ".//span[contains(@class,'CurrentPrice')]//span[contains(@class,'NumberPart')]")
        if candidates:
            txt = candidates[0].text.strip()
            if txt:
                return float(txt.replace(",", "").replace("$",""))
    except:
        pass

    try:
        all_num = section.find_elements(By.XPATH, ".//span[contains(@class,'NumberPart')]")
        for n in all_num:
            txt = n.text.strip()
            if re.match(r"^\d+(?:\.\d+)?$", txt):
                return float(txt.replace(",", ""))
    except:
        pass

    try:
        text = section.text
        m = re.search(r"\$?\s*([\d,]+(?:\.\d{1,2})?)", text)
        if m:
            return float(m.group(1).replace(",", ""))
    except:
        pass

    return None

# ------------------ Core Logic ------------------

def get_short_ending_listings(base_url, max_pages=10, min_seconds=180, max_seconds=300, max_ratio=0.2):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    page_number = 0
    saved_listings = []

    while page_number < max_pages:
        url = base_url + str(page_number)
        driver.get(url)
        scroll_to_load_all(driver)
        time.sleep(1)

        listings = driver.find_elements(By.CSS_SELECTOR, "section[data-listingid]")
        if not listings:
            break

        stop_pagination = False
        for section in listings:
            listing_id = section.get_attribute("data-listingid")
            try:
                link_el = section.find_element(By.CSS_SELECTOR, "h2.title a")
                link = link_el.get_attribute("href")
            except:
                link = None

            # countdown
            countdown_text, total_seconds = None, None
            try:
                spans = section.find_elements(By.CSS_SELECTOR, "p.time span")
                for sp in spans:
                    t = sp.text.strip()
                    if t and not t.lower().startswith("remaining") and not t.lower().startswith("ended"):
                        countdown_text = t
                        total_seconds = parse_countdown(countdown_text)
                        break
            except:
                pass

            # MSRP
            msrp_value = None
            try:
                anchors = section.find_elements(By.XPATH, ".//a")
                for a in anchors:
                    txt = a.text.strip()
                    if txt and "MSRP" in txt.upper():
                        msrp_value = parse_msrp(txt)
                        if msrp_value:
                            break
                if not msrp_value:
                    subs = section.find_elements(By.CSS_SELECTOR, "h3.subtitle, .subtitle")
                    for s in subs:
                        val = parse_msrp(s.text.strip())
                        if val:
                            msrp_value = val
                            break
            except:
                pass

            bid_value = parse_bid_value(section)

            if total_seconds is not None:
                if min_seconds <= total_seconds <= max_seconds:
                    if msrp_value and bid_value is not None and msrp_value > 0:
                        ratio = bid_value / msrp_value
                        if ratio < max_ratio:
                            saved_listings.append({
                                "id": listing_id,
                                "link": link,
                                "countdown": countdown_text,
                                "seconds_remaining": total_seconds,
                                "bid": bid_value,
                                "msrp": msrp_value,
                                "ratio": ratio
                            })
                elif total_seconds > max_seconds:
                    stop_pagination = True
                    break

        if stop_pagination:
            break

        page_number += 1

    driver.quit()
    return saved_listings

# ------------------ Public Function ------------------

def fetch_auction_listings(keywords=[], negative_keywords=[], max_pages=10, min_seconds=180, max_seconds=300, max_ratio=0.2):
    chosen_link = get_auction_links()
    auction_section_id = extract_auction_section_id(chosen_link)
    base_url = f"https://vistaauction.com/Event/Details/{auction_section_id}?ViewStyle=list&StatusFilter=active_only&SortFilterOptions=1&page="
    listings = get_short_ending_listings(base_url, max_pages, min_seconds, max_seconds, max_ratio)
    filtered = []
    for item in listings:
        link = item.get("link") or ""
        if keywords != []:  # must contain at least one keyword
            if any(kw.lower() in link.lower() for kw in keywords):
                filtered.append(item)
        elif negative_keywords != []:  # drop if contains any negative keyword
            if not any(nkw.lower() in link.lower() for nkw in negative_keywords):
                filtered.append(item)
        else:  # no filters -> keep all
            filtered.append(item)

    return filtered

# Example usage:
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, default="", help="Comma-separated keywords")
    parser.add_argument("--negative_keywords", type=str, default="", help="Comma-separated negative keywords")
    args = parser.parse_args()

    keywords = args.keywords.split(",") if args.keywords else []
    negative_keywords = args.negative_keywords.split(",") if args.negative_keywords else ["shirt", "jacket", "coat", "pant", "jean", "shorts", "sneaker", "shoe","glove", "mittens", "scarf"]
    results = fetch_auction_listings(keywords=keywords, negative_keywords=negative_keywords)
    print(json.dumps(results, indent=2))
