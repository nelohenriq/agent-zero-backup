import json
from pathlib import Path

def deep_search(obj, path="", found=None):
    if found is None:
        found = []
    if isinstance(obj, dict):
        # Check for match-like keys
        keys = set(obj.keys())
        if 'id' in keys and ('name' in keys or 'homeTeam' in keys or 'awayTeam' in keys or 'fixture' in keys):
            found.append((path, obj))
        for k, v in obj.items():
            deep_search(v, f"{path}.{k}", found)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            deep_search(item, f"{path}[{i}]", found)
    return found

files_to_check = [
    ('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_final_intercept_20260307_002759.json', 'data'),
    ('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_api_intercept_fixed_20260307_004801.json', 'full_body')
]

for file_path, key_name in files_to_check:
    p = Path(file_path)
    if not p.exists():
        print(f"File not found: {file_path}")
        continue
    
    print(f"\n--- Analyzing {p.name} (looking for '{key_name}') ---")
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"Root is list with {len(data)} items.")
            for i, item in enumerate(data):
                if key_name in item:
                    content = item[key_name]
                    print(f"Item {i} has '{key_name}'. Type: {type(content)}")
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                            print(f"  Parsed '{key_name}' as JSON.")
                        except:
                            print(f"  '{key_name}' is a string but not JSON.")
                            continue
                    
                    if isinstance(content, (dict, list)):
                        matches = deep_search(content)
                        print(f"  Found {len(matches)} potential match objects in this item.")
                        if matches:
                            print(f"  Sample match path: {matches[0][0]}")
                            print(f"  Sample match keys: {list(matches[0][1].keys())}")
                            # Print a snippet of the match
                            sample = matches[0][1]
                            print(f"  Sample data: {json.dumps(sample, indent=2)[:500]}...")
                            break # Stop after first successful find
        elif isinstance(data, dict):
            if key_name in data:
                content = data[key_name]
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except:
                        pass
                if isinstance(content, (dict, list)):
                    matches = deep_search(content)
                    print(f"Found {len(matches)} potential match objects.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
