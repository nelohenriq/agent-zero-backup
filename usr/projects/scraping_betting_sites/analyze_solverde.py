import json
import os

file_path = '/a0/usr/projects/scraping_betting_sites/solverde_api_intercept_final.json'

if not os.path.exists(file_path):
    print(f"Error: File {file_path} not found.")
    exit(1)

print(f"Loading data from {file_path}...")
with open(file_path, 'r', encoding='utf-8') as f:
    captured_data = json.load(f)

print(f"Loaded {len(captured_data)} API responses.\n")

for i, item in enumerate(captured_data):
    url = item['url']
    data = item['data']
    print(f"--- Response {i+1}: {url} ---")
    
    if isinstance(data, dict):
        top_keys = list(data.keys())
        print(f"Top-level keys: {top_keys}")
        
        betting_keywords = ['match', 'event', 'game', 'odds', 'selection', 'team', 'participant', 'fixture', 'league', 'sport']
        found = [k for k in top_keys if any(kw in k.lower() for kw in betting_keywords)]
        if found:
            print(f"Potential betting keys: {found}")
        
        for key in top_keys:
            val = data[key]
            if isinstance(val, list):
                print(f" -> Found list '{key}' with {len(val)} items.")
                if len(val) > 0 and isinstance(val[0], dict):
                    print(f" Sample keys: {list(val[0].keys())}")
                    snippet = json.dumps(val[0], indent=2, ensure_ascii=False, default=str)
                    print(f" Sample: {snippet[:300]}...")
                break
            elif isinstance(val, dict):
                print(f" -> Found nested dict '{key}'. Keys: {list(val.keys())[:5]}")
    
    elif isinstance(data, list):
        print(f"Data is a list with {len(data)} items.")
        if len(data) > 0:
            print(f" First item type: {type(data[0])}")
            if isinstance(data[0], dict):
                print(f" First item keys: {list(data[0].keys())}")
                snippet = json.dumps(data[0], indent=2, ensure_ascii=False, default=str)
                print(f" Sample: {snippet[:300]}...")
    else:
        print(f"Data type: {type(data)}")

print("\nAnalysis complete.")
