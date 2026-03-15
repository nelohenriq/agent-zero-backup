import json
import requests
import sys

file_path = '/a0/usr/projects/scraping_betting_sites/solverde_api_intercept_final.json'

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading file: {e}")
    sys.exit(1)

live_url = None
for item in data:
    if 'initialResources' in item.get('url', '') and 'pt_PT_desktop' in item.get('url', ''):
        config = item.get('data', {})
        if 'liveEndpointUrl' in config:
            live_url = config['liveEndpointUrl']
            print(f"Found liveEndpointUrl: {live_url}")
            break

if not live_url:
    print("liveEndpointUrl not found in captured data.")
    print("Scanning all keys for 'live' or 'event' patterns...")
    for item in data:
        url = item.get('url', '')
        data_obj = item.get('data', {})
        if isinstance(data_obj, dict):
            for k in data_obj.keys():
                if 'live' in k.lower() or 'event' in k.lower() or 'stream' in k.lower():
                    print(f"Potential match in {url}: key '{k}' = {str(data_obj[k])[:100]}")
    sys.exit(0)

print(f"\nAttempting to connect to: {live_url}")
headers = {
    'Accept': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    resp = requests.get(live_url, headers=headers, stream=True, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Connection successful. Reading stream...")
        count = 0
        for line in resp.iter_lines():
            if line:
                decoded = line.decode('utf-8', errors='ignore')
                print(f"{decoded}")
                count += 1
                if count >= 5:
                    print("... (stopping after 5 lines)")
                    break
    else:
        print(f"Connection failed with status {resp.status_code}")
        print(f"Response body: {resp.text[:200]}")
except Exception as e:
    print(f"Error during request: {e}")
