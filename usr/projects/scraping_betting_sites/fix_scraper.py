import json
import os

output_dir = 'processed_sports'
os.makedirs(output_dir, exist_ok=True)

# Load data
with open('placard_prefetch_response.json.bak', 'r') as f:
    data = json.load(f)

print("Data loaded.")

# Build Sport ID to Name Map
sport_map = {}
if 'sportsMetaInformation' in data:
    for meta_group in data['sportsMetaInformation']:
        if 'sportMetas' in meta_group:
            for sport in meta_group['sportMetas']:
                sid = sport.get('id')
                if sid:
                    sport_map[sid] = sport.get('name', sid) or sid

print(f"Mapped sports: {list(sport_map.keys())}")

sport_events = {}
total_events = 0

# Traverse: eventGroups -> groups -> events
event_groups = data.get('eventGroups', [])

for group in event_groups:
    sub_groups = group.get('groups', [])
    
    for sub_group in sub_groups:
        # Try to find sport ID in the sub_group itself
        sport_id = sub_group.get('sportId') or sub_group.get('sport') or sub_group.get('id')
        
        # If 'id' is a generic group ID, check if it matches a known sport
        if not sport_id:
            if 'sport' in sub_group and isinstance(sub_group['sport'], dict):
                sport_id = sub_group['sport'].get('id')
        
        if not sport_id and 'id' in sub_group:
            potential_id = sub_group['id']
            if potential_id in sport_map:
                sport_id = potential_id
        
        if not sport_id:
            # Debug: print keys to understand structure
            # print(f"Sub-group without sport ID. Keys: {list(sub_group.keys())}")
            # print(f"Sub-group ID: {sub_group.get('id')}")
            continue
        
        # Normalize sport_id
        if isinstance(sport_id, str):
            sport_id = sport_id.lower()
        
        if sport_id not in sport_map and sport_id not in sport_events:
            sport_map[sport_id] = sport_id
        
        events = sub_group.get('events', [])
        
        for event in events:
            if sport_id not in sport_events:
                sport_events[sport_id] = []
            
            event_copy = event.copy()
            event_copy['sportId'] = sport_id
            event_copy['sportName'] = sport_map.get(sport_id, sport_id)
            sport_events[sport_id].append(event_copy)
            total_events += 1

print(f"\nTotal events processed: {total_events}")
print(f"Sports found: {list(sport_events.keys())}")

# Write files
for sport_id, events in sport_events.items():
    filename = f"{output_dir}/placard_{sport_id}.json"
    with open(filename, 'w') as f:
        json.dump(events, f, indent=2)
    print(f"Written {len(events)} events to {filename}")

print("\n=== Final Summary ===")
for sport_id, events in sorted(sport_events.items()):
    print(f"{sport_id}: {len(events)} matches")
