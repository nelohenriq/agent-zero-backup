import requests
import json
import os
from datetime import datetime

# Target API endpoint identified from previous capture
API_URL = "https://mpc-prod-27-s6uit34pua-uk.a.run.app/events"

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    "Referer": "https://solverde.pt/",
    "Origin": "https://solverde.pt",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache"
}

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"solverde_extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

def fetch_data():
    print(f"Fetching data from {API_URL}...")
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def transform_to_hierarchical(data):
    """
    Transforms raw API data into the hierarchical structure:
    Country -> Competition -> Market -> Events
    """
    if not data:
        return {}

    hierarchy = {}
    
    # Attempt to locate the list of events/matches in the response
    # Common keys: 'events', 'matches', 'data', 'sports', 'competitions'
    events_list = []
    
    if isinstance(data, list):
        events_list = data
    elif isinstance(data, dict):
        # Try common keys
        for key in ['events', 'matches', 'data', 'sports', 'competitions', 'leagues']:
            if key in data:
                val = data[key]
                if isinstance(val, list):
                    events_list = val
                    break
                elif isinstance(val, dict) and 'items' in val:
                    events_list = val['items']
                    break
        
        # If no list found, check if the root is an object with event-like keys
        if not events_list and len(data) > 0:
            # Fallback: treat the whole dict as a single event or check nested structures
            pass

    print(f"Found {len(events_list)} potential events/items.")

    for item in events_list:
        if not isinstance(item, dict):
            continue

        # Extract fields with fallbacks
        country_name = item.get('country') or item.get('countryName') or item.get('competition', {}).get('country') or 'Unknown'
        competition_name = item.get('competition') or item.get('competitionName') or item.get('league') or 'Unknown'
        event_name = item.get('name') or item.get('homeTeam') + ' vs ' + item.get('awayTeam') if item.get('homeTeam') and item.get('awayTeam') else item.get('id') or 'Unknown Event'
        start_time = item.get('startTime') or item.get('start_time') or item.get('date') or 'Unknown'
        
        # Extract odds/markets
        markets = {}
        if 'odds' in item:
            markets = item['odds']
        elif 'markets' in item:
            markets = item['markets']
        elif 'bookmakers' in item:
            markets = item['bookmakers']
        else:
            # Try to find odds in nested structures
            for k, v in item.items():
                if isinstance(v, dict) and ('odds' in k or 'market' in k):
                    markets[k] = v

        # Ensure country exists in hierarchy
        if country_name not in hierarchy:
            hierarchy[country_name] = {}
        
        # Ensure competition exists
        if competition_name not in hierarchy[country_name]:
            hierarchy[country_name][competition_name] = {
                "events": [],
                "metadata": {
                    "country": country_name,
                    "competition": competition_name
                }
            }
        
        event_data = {
            "id": item.get('id') or item.get('eventId'),
            "name": event_name,
            "startTime": start_time,
            "homeTeam": item.get('homeTeam'),
            "awayTeam": item.get('awayTeam'),
            "markets": markets
        }
        
        hierarchy[country_name][competition_name]["events"].append(event_data)

    return hierarchy

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    raw_data = fetch_data()
    
    if not raw_data:
        print("Failed to fetch data. Saving error log.")
        with open(os.path.join(OUTPUT_DIR, "solverde_error_log.json"), 'w') as f:
            json.dump({"error": "Fetch failed", "timestamp": datetime.now().isoformat()}, f, indent=2)
        return

    # Save raw data for inspection
    raw_file = os.path.join(OUTPUT_DIR, f"solverde_raw_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)
    print(f"Raw response saved to {raw_file}")

    # Transform to hierarchical structure
    hierarchical_data = transform_to_hierarchical(raw_data)
    
    # Save hierarchical data
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(hierarchical_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nExtraction complete!")
    print(f"Hierarchical data saved to: {OUTPUT_FILE}")
    print(f"Countries found: {list(hierarchical_data.keys())}")
    
    # Print sample
    if hierarchical_data:
        first_country = list(hierarchical_data.keys())[0]
        first_comp = list(hierarchical_data[first_country].keys())[0]
        sample = {
            first_country: {
                first_comp: hierarchical_data[first_country][first_comp]
            }
        }
        print("\nSample Output (First Country/Competition):")
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:1000] + "...")

if __name__ == "__main__":
    main()
