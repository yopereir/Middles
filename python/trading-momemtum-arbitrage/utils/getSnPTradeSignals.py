import requests
from bs4 import BeautifulSoup
import json

def get_snp_trade_signals(url):
    """
    Webscrapes data from the specified URL, specifically targeting a table
    with class 'prnbcc', and stores each row as a JSON object in an array.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: A JSON string representation of the scraped data, or an error message.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to retrieve the webpage: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='prnbcc')

    if not table:
        raise ValueError("Table with class 'prnbcc' not found on the page.")

    data_rows = []
    headers = []

    # Get headers from the first row (th tags)
    header_row = table.find('tr')
    if header_row:
        headers = [th.get_text(strip=True) for th in header_row.find_all('th')]

    # Iterate over subsequent rows
    for row in table.find_all('tr')[1:]:  # Skip the header row
        columns = row.find_all(['td', 'th']) # Consider both td and th for robustness
        row_data = {}
        for i, col in enumerate(columns):
            if i < len(headers):
                row_data[headers[i]] = col.get_text(strip=True)
            else:
                # Handle cases where there might be more columns than headers
                match i:
                    case 0:
                        columnName = "Execution_Date"
                    case 1:
                        columnName = "Index_Name"
                    case 2:
                        columnName = "Action"
                    case 3:
                        columnName = "Company_Name"
                    case 4:
                        columnName = "Ticker"
                    case 5:
                        columnName = "GICS_Sector"
                    case _:
                        columnName = f"column_{i+1}"
                row_data[columnName] = col.get_text(strip=True)
        if row_data:  # Only add if the row is not empty
            data_rows.append(row_data)

    return json.dumps(data_rows, indent=4)

if __name__ == "__main__":
    # Example URL to scrape
    url = "https://press.spglobal.com/2025-07-02-Datadog-Set-to-Join-S-P-500"
    scraped_json = get_snp_trade_signals(url)
    print(scraped_json)