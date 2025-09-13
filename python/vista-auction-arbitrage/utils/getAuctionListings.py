from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

def get_auction_links():
    # ------------------ Setup Selenium options ------------------
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-gpu-compositing")
    options.add_argument("--disable-gcm")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(options=options)
    driver.get("https://vistaauction.com/?ViewFilter=Current")
    time.sleep(3)  # Wait for initial JS render

    # ------------------ Scroll until "Starts Closing In" appears ------------------
    for _ in range(20):
        if "Starts Closing In" in driver.page_source:
            break
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.5)
    else:
        driver.quit()
        raise RuntimeError("Could not find 'Starts Closing In' section after scrolling")

    # ------------------ Identify first and second sections ------------------
    first_section = None
    second_section = None

    # Find all cards containing 'Closing' or 'Starts Closing In'
    cards = driver.find_elements(By.XPATH, "//div[contains(., 'Closing') or contains(., 'Starts Closing In')]")

    for card in cards:
        text = card.text.upper()
        if "STARTS CLOSING IN" in text and second_section is None:
            second_section = card
        elif "CLOSING" in text and first_section is None:
            first_section = card

    if not first_section or not second_section:
        driver.quit()
        raise RuntimeError("Could not identify first and second sections")

    # Scroll second section into view so countdown renders
    driver.execute_script("arguments[0].scrollIntoView(true);", second_section)
    time.sleep(1)  # wait for JS

    # ------------------ Extract countdown from second section ------------------
    total_seconds = None
    try:
        countdown_el = second_section.find_element(By.XPATH,
            ".//span[contains(text(), 'Minutes') or contains(text(), 'Seconds')]")
        countdown_text = countdown_el.text
        m = re.search(r"(\d+)\s*Minutes?.*?(\d+)\s*Seconds?", countdown_text)
        if m:
            minutes = int(m.group(1))
            seconds = int(m.group(2))
            total_seconds = minutes * 60 + seconds
            print(f"Countdown: {minutes} min {seconds} sec ({total_seconds} sec)")
        else:
            print("Could not parse countdown text, defaulting to first section")
    except:
        print("Countdown element not found, defaulting to first section")

    # ------------------ Extract links ------------------
    def extract_link(section):
        try:
            # Pick the first <a> inside the section with /Event/Details/ in href
            link_el = section.find_element(By.XPATH, ".//a[contains(@href, '/Event/Details/')]")
            return link_el.get_attribute("href")
        except:
            return None

    first_link = extract_link(first_section)
    second_link = extract_link(second_section)

    driver.quit()

    # ------------------ Choose link based on countdown ------------------
    if total_seconds is not None and total_seconds < 20 * 60 and second_link:
        return second_link
    else:
        return first_link

# ------------------ Main ------------------
if __name__ == "__main__":
    chosen_link = get_auction_links()
    print("Chosen link:", chosen_link)

    # Extract auctionSectionID using regex
    import re
    match = re.search(r"/Event/Details/(\d+)", chosen_link)
    if match:
        auction_section_id = match.group(1)
        print("Auction Section ID:", auction_section_id)

        # Build new URL
        new_url = f"https://vistaauction.com/Event/Details/{auction_section_id}?ViewStyle=list&StatusFilter=active_only&SortFilterOptions=1&page=0"
        print("New URL:", new_url)
    else:
        print("Could not extract auctionSectionID from the chosen link.")

