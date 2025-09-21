# Usage: python utils/callAppScript.py "https://vistaauction.com/auctions/12345" 150
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # loaded once

def send_listing(listing_url: str, max_bid: float) -> dict:
    """
    Sends listing data to the Google Apps Script webhook.

    Args:
        listing_url (str): URL of the listing
        max_bid (float): Maximum bid value

    Returns:
        dict: Parsed JSON response from the webhook
    """
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL not set in .env file")

    data = {
        "listing_url": listing_url,
        "max_bid": max_bid
    }

    response = requests.post(WEBHOOK_URL, data=data)

    try:
        return response.json()  # parse JSON response
    except requests.JSONDecodeError:
        # If server returned HTML or something unexpected
        return {
            "status_code": response.status_code,
            "text": response.text
        }
if __name__ == "__main__":
    # Example usage
    test_url = "https://vistaauction.com/auctions/12345"
    test_max_bid = 150.00
    result = send_listing(test_url, test_max_bid)
    print(result)