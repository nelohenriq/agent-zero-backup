import json

with open('processed_sports/solverde_api_capture_full_20260307_001048.json') as f:
 data = json.load(f)

print(f'Total API responses: {len(data)}')

# Search for match/odds data in responses
for resp in data:
 url = resp.get('url', '')
 
 # Filter for relevant URLs
 keywords = ['sport', 'bet', 'odd', 'game', 'event', 'match', 'live', 'football', 'soccer', 'futebol']
 if any(x in url.lower() for x in keywords):
 print(f'\n=== {url} ===')
 body = resp.get('data', {})
 if isinstance(body, dict):
 print(f'Keys: {list(body.keys())[:20]}')
 # Check for match/competition data
 for k in body.keys():
 v = body[k]
 if isinstance(v, list) and len(v) > 0:
 print(f' {k}: list[{len(v)}], sample: {str(v[0])[:100]}')
 elif isinstance(v, dict) and len(v) > 0:
 print(f' {k}: dict, keys: {list(v.keys())[:10]}')
 elif isinstance(v, str) and len(v) > 100:
 print(f' {k}: str[{len(v)}], preview: {v[:150]}')

# Also check the live captured data
print('\n\n=== Checking solverde_live_captured_data.json ===')
with open('processed_sports/solverde_live_captured_data.json') as f:
 live_data = json.load(f)
print(f'Keys: {list(live_data.keys())}')
if 'data' in live_data:
 data2 = live_data['data']
 print(f'data keys: {list(data2.keys())[:15]}')
