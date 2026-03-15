import json

with open('/a0/usr/projects/scraping_betting_sites/placard_prefetch_response.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== TOP-LEVEL KEYS ===")
print(list(data.keys()))
print()

print("=== SPORTS META INFORMATION ===")
if 'sportsMetaInformation' in data:
    sports = data['sportsMetaInformation']
    print(f"Type: {type(sports)}")
    print(f"Number of sports: {len(sports)}")
    for sport_info in sports:
        print(f"  Sport: {sport_info}")
print()

print("=== EVENTS STRUCTURE ===")
if 'events' in data:
    events = data['events']
    print(f"Type: {type(events)}")
    if isinstance(events, list):
        print(f"Total events: {len(events)}")
        if events:
            print(f"Sample event keys: {list(events[0].keys())}")
    elif isinstance(events, dict):
        print(f"Total events: {len(events)}")
print()

print("=== UNIQUE SPORT IDs IN EVENTS ===")
if 'events' in data and isinstance(data['events'], list):
    sport_ids = set()
    for event in data['events']:
        sport_id = event.get('sportId', 'N/A')
        sport_ids.add(str(sport_id))
    print(f"Unique sportIds: {sorted(sport_ids)}")

print()
print("=== SAMPLE EVENTS BY SPORT ===")
for sid in sorted(sport_ids):
    events_for_sport = [e for e in data['events'] if str(e.get('sportId')) == sid]
    if events_for_sport:
        e = events_for_sport[0]
        print(f"SportID {sid}: {e.get('name')} | Competition: {e.get('className')} | Type: {e.get('typeName')}")

print()
print("=== MARKETS STRUCTURE ===")
if 'markets' in data:
    markets = data['markets']
    print(f"Type: {type(markets)}")
    if isinstance(markets, dict):
        print(f"Number of markets: {len(markets)}")
        first_key = list(markets.keys())[0]
        print(f"Sample market key: {first_key}")
        print(f"Sample market keys: {list(markets[first_key].keys())[:10]}")
