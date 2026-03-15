import json

# Load the WebSocket frames
with open('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_ws_v8_20260307_164139.json') as f:
    data = json.load(f)

recv = data.get('frames_received', [])

# Function to extract JSON from frame text (skip headers)
def extract_json_payload(frame_text):
    # Find the JSON start (after headers)
    lines = frame_text.split('\n')
    json_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            json_start = i
            break
    if json_start >= 0:
        json_text = '\n'.join(lines[json_start:])
        try:
            return json.loads(json_text)
        except:
            pass
    return None

# Key frames to analyze
key_frames = [5, 6, 8, 9]
all_matches = []
all_odds = {}

for idx in key_frames:
    if idx < len(recv):
        frame = recv[idx]
        txt = frame.get('text', '')
        payload = extract_json_payload(txt)
        
        if payload:
            print(f"\n=== FRAME {idx} - FULL PAYLOAD ===")
            print(f"Keys: {list(payload.keys())}")
            
            # Extract items
            items = payload.get('items', [])
            if items:
                print(f"\nFound {len(items)} items in Frame {idx}")
                for item in items[:5]:  # First 5
                    print(f"  - {item.get('name', item.get('id', 'N/A'))}")
                    all_matches.append(item)
            
            # Extract event groups
            if 'eventGroups' in payload:
                eg = payload['eventGroups']
                print(f"\nEventGroups: {json.dumps(eg, indent=2)[:1000]}")
                all_matches.extend(eg if isinstance(eg, list) else [eg])
            
            # Check for selections/odds
            if 'selections' in payload:
                print(f"\n--- Betting Selections in Frame {idx} ---")
                for sel in payload['selections']:
                    print(f"  Selection: {sel.get('name')} -> Odds: {sel.get('odds')}")
                    all_odds[sel.get('id')] = sel

# Also check frames 69, 71 for betting data
for idx in [69, 71]:
    if idx < len(recv):
        frame = recv[idx]
        txt = frame.get('text', '')
        payload = extract_json_payload(txt)
        if payload:
            print(f"\n=== FRAME {idx} - BETTING SELECTIONS ===")
            if 'selections' in payload:
                for sel in payload['selections']:
                    print(f"  {sel.get('name')}: {sel.get('odds')}")

# Save extracted data
output = {
    'matches_found': len(all_matches),
    'bets_found': len(all_odds),
    'sample_matches': all_matches[:20],
    'sample_odds': list(all_odds.values())[:20]
}

with open('/a0/usr/projects/scraping_betting_sites/processed_sports/extracted_betting_data.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n=== SUMMARY ===")
print(f"Total matches extracted: {len(all_matches)}")
print(f"Total betting selections: {len(all_odds)}")
print("Saved to: processed_sports/extracted_betting_data.json")
