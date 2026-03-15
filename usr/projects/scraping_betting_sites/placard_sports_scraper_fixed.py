import json
import sys
from curl_cffi import requests

# Placard API Configuration
BASE_URL = "https://api.placard.pt"
SPORTS_ENDPOINT = "/sports"

# Required Headers to emulate Chrome 124 and bypass 403/405
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.placard.pt",
    "Referer": "https://www.placard.pt/",
    "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Connection": "keep-alive",
    "Priority": "u=1, i"
}

def fetch_sports_data():
    """
    Fetches sports data from Placard API.
    Handles 405 errors by ensuring correct HTTP method and headers.
    """
    url = f"{BASE_URL}{SPORTS_ENDPOINT}"
    
    try:
        # Using GET method as per standard API patterns for fetching lists
        # If 405 occurs, it implies the server expects POST, but usually GET is correct for /sports
        # We will try GET first with strict headers.
        response = requests.get(url, headers=HEADERS, impersonate="chrome124", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 405:
            print("Error 405: Method Not Allowed. The endpoint might require POST or a different path.")
            # Fallback: Try POST if GET fails with 405 (common in some APIs)
            print("Attempting POST method as fallback...")
            response = requests.post(url, headers=HEADERS, json={}, impersonate="chrome124", timeout=30)
            print(f"POST Status Code: {response.status_code}")
            
        if response.status_code == 200:
            try:
                data = response.json()
                print("JSON parsing successful.")
                return data
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Raw Response Preview: {response.text[:500]}")
                return None
        else:
            print(f"Request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"An error occurred during the request: {e}")
        return None

def main():
    print("Starting Placard Sports Scraper...")
    data = fetch_sports_data()
    
    if data:
        # Save to file
        output_file = "/a0/usr/projects/scraping_betting_sites/placard_fixed_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {output_file}")
        
        # Basic validation
        if isinstance(data, list):
            print(f"Data is a list with {len(data)} items.")
        elif isinstance(data, dict):
            print(f"Data is a dict with keys: {list(data.keys())}")
        else:
            print(f"Data type: {type(data)}")
    else:
        print("Failed to retrieve data.")
        sys.exit(1)

if __name__ == "__main__":
    main()
