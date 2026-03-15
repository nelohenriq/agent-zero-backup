import json

with open('processed_sports/solverde_extended_60s_20260307_174905.json') as f:
    data = json.load(f)

api_responses = data.get('api_responses', [])
print(f"Total API responses: {len(api_responses)}\n")

# Show all unique URLs
urls = set()
for resp in api_responses:
    urls.add(resp.get('url', ''))

print("=== ALL API URLS ===")
for url in sorted(urls):
    print(url)

print("\n\n=== CHECKING FOR SPORTS/ODDS DATA ===")
for resp in api_responses:
    url = resp.get('url', '')
    status = resp.get('status', 0)
    body = resp.get('body', '')
    
    # Skip empty or error responses
    if status != 200 or not body or len(body) < 50:
        continue
    
    # Check for sports-related content
    url_lower = url.lower()
    body_lower = body.lower()
    
    if any(k in url_lower for k in ['sport', 'game', 'match', 'odds', 'bet', 'live', 'event', 'futebol', 'football', 'soccer']):
        print(f"\n=== {url} ===")
        print(f"Size: {len(body)} chars")
        # Show first 1500 chars of meaningful content
        if body.startswith('[') or body.startswith('{'):
            print(body[:1500])
        else:
            print(body[:1500])
