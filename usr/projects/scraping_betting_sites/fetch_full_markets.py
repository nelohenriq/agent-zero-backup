
import requests
import json
import uuid

def fetch_full_markets(event_id):
    # 1. Fetch market structure
    url = f"https://sportswidget-cdn.placard.pt/pre-fetch?locale=pt_PT&page=event&eventId={event_id}&type=DESKTOP"
    print(f"Fetching market structure for {event_id}...")
    res = requests.get(url)
    markets = res.json().get('markets', [])

    # 2. Fetch odds (Note: using the identified multi endpoint if available, 
    # otherwise falling back to mapping from a separate fetch or homepage pre-fetch)
    # For this PoC, we demonstrate the extraction of all market names.

    print(f"Found {len(markets)} markets.")
    for m in markets[:10]:
        print(f"Market: {m.get('name')} ({m.get('id')})")
        for s in m.get('selections', []):
            # In a full implementation, odds would be merged here from the /markets/multi call
            print(f"  - {s.get('name')}: {s.get('odds')}")

if __name__ == '__main__':
    fetch_full_markets('12561047983')
