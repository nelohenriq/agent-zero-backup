import json
import gzip
import os

file_path = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_live_captured_data.json'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Analyzing {len(data)} captured responses...")

sports_data_found = None
sports_url = None
sports_index = -1

for i, item in enumerate(data):
    url = item.get('url', '')
    body = item.get('body', '')
    status = item.get('status', 0)
    
    content = None
    try:
        if isinstance(body, str) and body.strip().startswith('{'):
            content = json.loads(body)
        elif isinstance(body, bytes):
            try:
                decompressed = gzip.decompress(body)
                content = json.loads(decompressed.decode('utf-8'))
            except:
                content = json.loads(body.decode('utf-8'))
    except Exception as e:
        continue
    
    if content:
        keys = set(content.keys()) if isinstance(content, dict) else set()
        sports_keys = {'events', 'competitions', 'sports', 'data', 'matches', 'odds', 'leagues'}
        
        found = False
        if isinstance(content, dict) and (keys & sports_keys):
            print(f"\n[FOUND] Sports data (dict) at index {i}: {url}")
            print(f"Keys: {list(keys)}")
            sports_data_found = content
            sports_url = url
            sports_index = i
            found = True
        elif isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
            first_item_keys = set(content[0].keys())
            if first_item_keys & sports_keys:
                print(f"\n[FOUND] Sports data (list) at index {i}: {url}")
                print(f"First item keys: {list(first_item_keys)}")
                sports_data_found = content
                sports_url = url
                sports_index = i
                found = True
        
        if found:
            break

if sports_data_found:
    print(f"\n=== Saving extracted sports data ===")
    output_path = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_raw_sports_data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sports_data_found, f, indent=2, ensure_ascii=False)
    print(f"Saved raw sports data to {output_path}")
    print(f"Data size: {len(json.dumps(sports_data_found))} bytes")
else:
    print("\n[NOT FOUND] No obvious sports data structure found in the captured responses.")
    print("Will need to re-capture with Playwright targeting mpc-prod endpoints.")
