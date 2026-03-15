import json

with open('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_ws_v8_20260307_164139.json') as f:
    data = json.load(f)

recv = data.get('frames_received', [])

# Extract sports list from frame 5
frame_5 = recv[5]['text']
double_nl = frame_5.find('\n\n')
json_text = frame_5[double_nl+2:]
sports = json.loads(json_text)

print('=== AVAILABLE SPORTS ===')
for item in sports.get('items', []):
    print(f"  {item.get('id')}: {item.get('name')} ({item.get('canonicalName')})")

# Look at frame 6 for in-play data
print('\n=== FRAME 6 (IN-PLAY) ===')
frame_6 = recv[6]['text']
double_nl = frame_6.find('\n\n')
if double_nl > 0:
    payload = json.loads(frame_6[double_nl+2:])
    print(f"Keys: {list(payload.keys())}")
    if 'items' in payload:
        print(f"Items count: {len(payload['items'])}")
        if payload['items']:
            first = payload['items'][0]
            print(f"First item keys: {list(first.keys())}")
            print(f"Sample: {json.dumps(first, ensure_ascii=False)[:800]}")

# Look at frame 8 for event groups
print('\n=== FRAME 8 (EVENT GROUPS) ===')
frame_8 = recv[8]['text']
double_nl = frame_8.find('\n\n')
if double_nl > 0:
    payload = json.loads(frame_8[double_nl+2:])
    print(f"Keys: {list(payload.keys())}")
    if 'items' in payload:
        print(f"Event groups count: {len(payload['items'])}")
        for item in payload['items'][:3]:
            print(f"  - {item.get('name', item.get('id', 'unknown'))}")
