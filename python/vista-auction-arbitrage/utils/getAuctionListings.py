# getAuctionListings.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, subprocess, re

# ------------------ Step 1: Get main auction link ------------------
def get_auction_links():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get("https://vistaauction.com/?ViewFilter=Current")
    time.sleep(3)

    # Scroll until "Starts Closing In" appears
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

# ------------------ Step 2: Extract auctionSectionID ------------------
def extract_auction_section_id(url):
    match = re.search(r"/Event/Details/(\d+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Could not extract auctionSectionID")

# ------------------ Step 3: Scroll helper ------------------
def scroll_to_load_all(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ------------------ Step 4: Parse countdown from text ------------------
def parse_countdown(text):
    if not text:
        return None
    m = re.search(r"(\d+)\s*Minute[s]?,?\s*(\d+)\s*Second[s]?", text, re.IGNORECASE)
    if m:
        minutes = int(m.group(1))
        seconds = int(m.group(2))
        return minutes*60 + seconds
    # handle single component like "1 Minute" or "42 Seconds"
    m2 = re.search(r"(\d+)\s*Minute[s]?", text, re.IGNORECASE)
    if m2:
        return int(m2.group(1)) * 60
    m3 = re.search(r"(\d+)\s*Second[s]?", text, re.IGNORECASE)
    if m3:
        return int(m3.group(1))
    return None

# ------------------ Step 5: Parse MSRP from anchor/subtitle text ------------------
def parse_msrp(text):
    if not text:
        return None
    # Normalize whitespace
    txt = " ".join(text.split())
    # Try common patterns: "MSRP: $40.0" or "$40.0" near "MSRP"
    m = re.search(r"MSRP[:\s]*\$?([\d,]+(?:\.\d+)?)", txt, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except:
            return None
    # fallback: find any $NN or NN.NN that appears with 'MSRP' elsewhere
    m2 = re.search(r"\$([\d,]+(?:\.\d+)?)", txt)
    if m2:
        try:
            return float(m2.group(1).replace(",", ""))
        except:
            return None
    # fallback: just a bare number (not ideal, but try)
    m3 = re.search(r"(\d+(?:\.\d{1,2})?)", txt)
    if m3:
        try:
            return float(m3.group(1))
        except:
            return None
    return None

# ------------------ Step 6: Extract bid price robustly ------------------
def parse_bid_value(section):
    # Try specific CurrentPrice NumberPart first
    try:
        candidates = section.find_elements(By.XPATH, ".//span[contains(@class,'CurrentPrice')]//span[contains(@class,'NumberPart')]")
        if candidates:
            txt = candidates[0].text.strip()
            if txt:
                return float(txt.replace(",", "").replace("$",""))
    except:
        pass

    # Fallback: look for any NumberPart under the section, prefer those near price classes
    try:
        all_num = section.find_elements(By.XPATH, ".//span[contains(@class,'NumberPart')]")
        for n in all_num:
            txt = n.text.strip()
            if re.match(r"^\d+(?:\.\d+)?$", txt):
                return float(txt.replace(",", ""))
    except:
        pass

    # Another fallback: search for a $NN pattern anywhere inside the section text
    try:
        text = section.text
        m = re.search(r"\$?\s*([\d,]+(?:\.\d{1,2})?)", text)
        if m:
            return float(m.group(1).replace(",", ""))
    except:
        pass

    return None

# ------------------ Step 7: Get 3–5 min listings with bid/msrp < 20% ------------------
def get_short_ending_listings(base_url, max_pages=10):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    page_number = 0
    saved_listings = []

    while page_number < max_pages:
        url = base_url + str(page_number)
        print(f"\n=== Loading page {page_number}: {url} ===")
        driver.get(url)
        scroll_to_load_all(driver)
        time.sleep(1)

        listings = driver.find_elements(By.CSS_SELECTOR, "section[data-listingid]")
        if not listings:
            print("No listings found on this page. Ending pagination.")
            break

        stop_pagination = False
        for idx, section in enumerate(listings):
            listing_id = section.get_attribute("data-listingid")
            try:
                link_el = section.find_element(By.CSS_SELECTOR, "h2.title a")
                link = link_el.get_attribute("href")
            except:
                link = "Link not found"

            # Countdown
            countdown_text = None
            total_seconds = None
            try:
                # pick the first span inside p.time that has visible text (the time string)
                spans = section.find_elements(By.CSS_SELECTOR, "p.time span")
                for sp in spans:
                    t = sp.text.strip()
                    if t and not t.lower().startswith("remaining") and not t.lower().startswith("ended"):
                        countdown_text = t
                        total_seconds = parse_countdown(countdown_text)
                        break
            except:
                pass

            # MSRP: search anchors first (likely contains MSRP), then subtitle h3
            msrp_value = None
            try:
                anchors = section.find_elements(By.XPATH, ".//a")
                for a in anchors:
                    txt = a.text.strip()
                    if not txt:
                        continue
                    if "MSRP" in txt.upper() or "MSRP" in txt:
                        msrp_value = parse_msrp(txt)
                        if msrp_value:
                            break
                # fallback: subtitle or h3
                if not msrp_value:
                    subs = section.find_elements(By.CSS_SELECTOR, "h3.subtitle, .subtitle")
                    for s in subs:
                        val = parse_msrp(s.text.strip())
                        if val:
                            msrp_value = val
                            break
            except:
                msrp_value = None

            # BID
            bid_value = parse_bid_value(section)

            # Debug print
            ratio_str = "N/A"
            try:
                if bid_value is not None and msrp_value:
                    ratio = bid_value / msrp_value if msrp_value != 0 else None
                    ratio_str = f"{ratio:.4f}" if ratio is not None else "N/A"
                else:
                    ratio_str = "N/A"
            except:
                ratio_str = "N/A"

            print(f"Listing {idx} | ID={listing_id} | Countdown={countdown_text or 'N/A'} | BID={bid_value} | MSRP={msrp_value} | ratio={ratio_str} | Link={link}")

            # Apply filters:
            # 1) countdown between 180 and 300 seconds
            # 2) bid/msrp < 0.2  (must have both bid and msrp)
            if total_seconds is not None:
                if 180 <= total_seconds <= 300:
                    if msrp_value and bid_value is not None and msrp_value > 0:
                        ratio = bid_value / msrp_value
                        if ratio < 0.2:
                            print(" -> Passed filter (3-5m & ratio<0.2). Adding.")
                            saved_listings.append(link)
                        else:
                            print(f" -> Ratio {ratio:.3f} >= 0.2, skipping.")
                    else:
                        print(" -> Missing bid or msrp, skipping.")
                elif total_seconds > 300:
                    stop_pagination = True
                    print("Found listing >5 minutes, stopping pagination.")
                    break
                else:
                    # total_seconds < 180 => ignore but continue
                    pass

        if stop_pagination:
            break

        page_number += 1

    driver.quit()
    return saved_listings

# ------------------ Main ------------------
if __name__ == "__main__":
    chosen_link = get_auction_links()
    print("Chosen link:", chosen_link)

    auction_section_id = extract_auction_section_id(chosen_link)
    print("Auction Section ID:", auction_section_id)

    base_url = f"https://vistaauction.com/Event/Details/{auction_section_id}?ViewStyle=list&StatusFilter=active_only&SortFilterOptions=1&page="

    listings = get_short_ending_listings(base_url)
    print("\nListings with 3–5 minutes remaining and bid/msrp < 20%:")
    for l in listings:
        print(l)
        # asynchronous call to tradeSignalAlgorithm.py
        subprocess.Popen(["python", "./utils/tradeSignalAlgorithm.py", l])
