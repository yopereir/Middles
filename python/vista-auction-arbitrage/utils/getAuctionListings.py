from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

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
    import re
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
    m = re.search(r"(\d+)\s*Minute[s]?,?\s*(\d+)\s*Second[s]?", text, re.IGNORECASE)
    if m:
        minutes = int(m.group(1))
        seconds = int(m.group(2))
        return minutes*60 + seconds
    return None

# ------------------ Step 5: Get 3–5 min listings ------------------
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

            # Extract countdown from first span inside p.time
            try:
                countdown_el = section.find_element(By.CSS_SELECTOR, "p.time span:first-child")
                countdown_text = countdown_el.text.strip()
                total_seconds = parse_countdown(countdown_text)
            except:
                total_seconds = None

            print(f"Listing {idx} | ID={listing_id} | Countdown={countdown_text if total_seconds else 'N/A'} | Link={link}")

            # Track only 3–5 min listings
            if total_seconds is not None:
                if 180 <= total_seconds <= 300:
                    saved_listings.append(link)
                elif total_seconds > 300:
                    stop_pagination = True
                    break

        if stop_pagination:
            print("Found listing >5 minutes, stopping pagination.")
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
    print("\nListings with 3–5 minutes remaining:")
    for l in listings:
        print(l)
