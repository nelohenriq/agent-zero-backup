"""
Investigation Results: Placard.pt Pre-Match & All Markets

1. EVENT DISCOVERY (Match List)
   - REST URL: https://sportswidget.placard.pt/api/eventgroups/soccer-all-match-events
   - Method: GET
   - WS Topic: /api/eventgroups/soccer-all-match-events
   - Headers:
       Host: sportswidget.placard.pt
       Accept: application/json
       Origin: https://www.placard.pt
   - Sample Structure:
     {
       "id": "soccer-all-match-events",
       "events": [
         { "id": "12609255715", "name": "Central Coast - Newcastle", "startTime": "..." }
       ]
     }

2. MARKET EXTRACTION (Full Markets)
   - REST URL: https://sportswidget.placard.pt/api/markets/multi
   - Method: POST
   - Payload: ["market_id_1", "market_id_2", ...]
   - WS Topic: /api/markets/<market_id>
   - Market Groups: Golos, Handicap, Partes, Cantos, etc.
   - Sample Structure (Market Object):
     {
       "id": "12609255869",
       "name": "Total de golos",
       "selections": [
         { "id": "s1", "name": "Mais de 2.5", "odds": 1.85 },
         { "id": "s2", "name": "Menos de 2.5", "odds": 1.95 }
       ]
     }

3. PREDICTABLE API CALLS
   - Get Event Details: GET https://sportswidget.placard.pt/api/events/<event_id>
   - Get Multiple Markets: POST https://sportswidget.placard.pt/api/markets/multi (Payload: JSON array of IDs)
"""

import requests
import json

def fetch_pre_match_soccer():
    url = "https://sportswidget.placard.pt/api/eventgroups/soccer-all-match-events"
    headers = {"Origin": "https://www.placard.pt", "Accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_markets(market_ids):
    url = "https://sportswidget.placard.pt/api/markets/multi"
    headers = {"Content-Type": "application/json", "Origin": "https://www.placard.pt"}
    response = requests.post(url, headers=headers, json=market_ids)
    return response.json()

if __name__ == "__main__":
    # Example Usage
    print("Investigation script for Placard.pt Pre-match Events & Markets")
    # events = fetch_pre_match_soccer()
    # print(f"Found {len(events.get('events', []))} events")
