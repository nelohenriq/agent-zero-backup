import json
import os

file_path = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_raw_debug.json'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total items: {len(data)}")
print("\nAnalyzing structure of first 3 items:")

for i, item in enumerate(data[:3]):
    print(f"\n--- Item {i} ---")
    print(f"Keys: {list(item.keys())}")
    if 'url' in item:
        print(f"URL: {item['url']}")
    
    # Check common content keys
    for key in ['content', 'body', 'response', 'data', 'payload', 'result', 'json']:
        if key in item:
            val = item[key]
            print(f" Found '{key}': type={type(val).__name__}, len={len(val) if hasattr(val, '__len__') else 'N/A'}")
            if isinstance(val, str) and len(val) > 100:
                print(f" Snippet: {val[:100]}...")
            elif isinstance(val, dict):
                print(f" Snippet keys: {list(val.keys())[:5]}")
            elif val is None:
                print(f" '{key}' is None")
        else:
            # print(f" '{key}' not found")
            pass

# Specifically look for the games/pt_PT item and print its full structure
print("\n--- Searching for games/pt_PT ---")
for item in data:
    url = item.get('url', '')
    if 'games/pt_PT' in url:
        print(f"Found: {url}")
        print(f"Full item keys: {list(item.keys())}")
        for k, v in item.items():
            if k != 'url' and k != 'timestamp':
                print(f"  Key '{k}': type={type(v).__name__}")
                if isinstance(v, dict):
                    print(f"    Sub-keys: {list(v.keys())[:10]}")
                elif isinstance(v, list):
                    print(f"    Length: {len(v)}")
                elif isinstance(v, str) and len(v) > 50:
                    print(f"    Snippet: {v[:50]}...")
        break
