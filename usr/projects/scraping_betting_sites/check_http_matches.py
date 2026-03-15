import json

# Check the main HTTP capture
with open('processed_sports/solverde_api_capture_full_20260307_001048.json') as f:
    data = json.load(f)

responses = data.get('responses', [])
print(f'Total HTTP responses: {len(responses)}')

# Search for match/odds data in responses
for resp in responses[:30]:
    url = resp.get('url', '')
    if any(x in url for x in ['sport', 'bet', 'odd', 'game', 'event', 'match', 'live', 'football']):
        print(f'\n=== {url} ===')
        body = resp.get('response', {}).get('body', {})
        if isinstance(body, dict):
            print(f'Keys: {list(body.keys())[:15]}')
            # Look for nested sports data
            for k in body.keys():
                v = body[k]
                if isinstance(v, (list, dict)) and len(str(v)) > 50:
                    print(f'  {k}: {type(v).__name__}, len={len(str(v))}')

# Also check the live captured data
print('\n\n=== Checking solverde_live_captured_data.json ===')
with open('processed_sports/solverde_live_captured_data.json') as f:
    live_data = json.load(f)
print(f'Keys: {list(live_data.keys())}')
for k in live_data.keys():
    v = live_data[k]
    print(f'{k}: {type(v).__name__}')
