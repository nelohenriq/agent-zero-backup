
import json
import time
import re
import os
from curl_cffi import requests

# Configuration
BASE_URL = "https://api.placard.bet"
OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.placard.bet/",
    "Origin": "https://www.placard.bet",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Connection": "keep-alive",
}

def sanitize_filename(name):
    """Sanitize string for use as filename."""
    # Remove or replace characters that are invalid in filenames
    # Specifically handling backslashes and forward slashes
    safe_name = re.sub(r'[^\w\s-]', '', name)
    safe_name = safe_name.strip().lower()
    safe_name = safe_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    return safe_name

def fetch_sports():
    """Fetch list of sports from the API."""
    print("Fetching sports list...")
    try:
        # Using the endpoint that returns the sports tree
        url = f"{BASE_URL}/sports"
        resp = requests.get(url, headers=HEADERS, impersonate="chrome124", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching sports: {e}")
        return []

def fetch_events(sport_id, sport_name):
    """Fetch events for a specific sport."""
    print(f"Fetching events for {sport_name} (ID: {sport_id})...")
    try:
        # Construct the URL for events. Adjust based on actual API structure if known.
        # Assuming a structure like /sports/{id}/events or similar
        # If the API requires a specific query parameter, adjust here.
        # Based on typical betting APIs, it might be /events?sport_id={id}
        url = f"{BASE_URL}/events?sport_id={sport_id}"

        resp = requests.get(url, headers=HEADERS, impersonate="chrome124", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching events for {sport_name}: {e}")
        return []

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sports_list = fetch_sports()

    if not sports_list:
        print("No sports found or error fetching sports.")
        return

    print(f"Found {len(sports_list)} sports.")
    results = {}

    for sport in sports_list:
        sport_id = sport.get("id")
        sport_name = sport.get("name", "Unknown")

        if not sport_id:
            continue

        events_list = fetch_events(sport_id, sport_name)

        # Sanitize filename
        safe_name = sanitize_filename(sport_name)
        filename = os.path.join(OUTPUT_DIR, f"placard_{safe_name}.json")

        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(events_list, f, indent=2, ensure_ascii=False)

        print(f" -> Saved {len(events_list)} matches to {filename}")
        results[sport_name] = len(events_list)

        time.sleep(0.5) # Rate limiting

    print(f"\n=== Summary ===")
    total = 0
    for name, count in results.items():
        print(f"{name}: {count} matches")
        total += count
    print(f"Total matches saved: {total}")

if __name__ == "__main__":
    main()
