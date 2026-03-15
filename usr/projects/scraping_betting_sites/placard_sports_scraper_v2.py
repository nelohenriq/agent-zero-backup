import json
import requests
import os
from datetime import datetime

# Working endpoint confirmed from previous successful runs
API_URL = "https://sportswidget-cdn.placard.pt/pre-fetch"

def fetch_prefetch_data():
    print(f"Fetching data from {API_URL}...")
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        # Verify it's JSON
        data = response.json()
        print(f"Successfully fetched data. Keys: {list(data.keys())}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON")
        return None

def process_sports(data):
    if not data or 'eventGroups' not in data:
        print("No valid eventGroups found in data.")
        return

    # Map sport names to their data
    sport_matches = {}

    for group in data.get('eventGroups', []):
        group_id = group.get('id', '')
        # Determine sport from group ID (e.g., 'soccer-...', 'basketball-...')
        sport_name = None
        if group_id.startswith('soccer-'):
            sport_name = 'soccer'
        elif group_id.startswith('basketball-'):
            sport_name = 'basketball'
        elif group_id.startswith('tennis-'):
            sport_name = 'tennis'
        elif group_id.startswith('hockey-'):
            sport_name = 'hockey'
        elif group_id.startswith('volleyball-'):
            sport_name = 'volleyball'
        elif group_id.startswith('esports-'):
            sport_name = 'esports'
        else:
            # Fallback: try to extract from first event if available
            if 'groups' in group and len(group['groups']) > 0:
                first_group = group['groups'][0]
                if 'typeId' in first_group:
                    tid = first_group['typeId']
                    if tid.startswith('soccer-'):
                        sport_name = 'soccer'
                    elif tid.startswith('basketball-'):
                        sport_name = 'basketball'
                    elif tid.startswith('tennis-'):
                        sport_name = 'tennis'
                    # Add more as needed

        if not sport_name:
            continue

        if sport_name not in sport_matches:
            sport_matches[sport_name] = {
                "sport": sport_name,
                "sportNumericId": 0,
                "scrapedAt": datetime.utcnow().isoformat(),
                "sourceUrl": API_URL,
                "matchCount": 0,
                "matches": []
            }

        # Process events in this group
        if 'groups' in group:
            for sub_group in group['groups']:
                if 'events' in sub_group:
                    for event in sub_group['events']:
                        match_data = {
                            "id": event.get('id'),
                            "name": event.get('name'),
                            "startTime": event.get('startTime'),
                            "sportId": sport_name,
                            "classId": sub_group.get('classId'),
                            "className": sub_group.get('className'),
                            "typeId": sub_group.get('typeId'),
                            "typeName": sub_group.get('typeName'),
                            "marketLines": event.get('marketLines', {})
                        }
                        sport_matches[sport_name]['matches'].append(match_data)

        # Update match count
        sport_matches[sport_name]['matchCount'] = len(sport_matches[sport_name]['matches'])

    # Save each sport to a separate file
    for sport, data in sport_matches.items():
        filename = f"placard_{sport}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {data['matchCount']} matches to {filename}")

    return sport_matches

def main():
    print("Starting Placard Sports Scraper (CDN Version)")
    data = fetch_prefetch_data()
    if data:
        results = process_sports(data)
        if results:
            print("\nSummary:")
            for sport, info in results.items():
                print(f"- {sport.capitalize()}: {info['matchCount']} matches")
        else:
            print("No sports data processed.")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()
