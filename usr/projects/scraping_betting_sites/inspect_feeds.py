import json
import os

INPUT_FILE = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_raw_debug.json'

if not os.path.exists(INPUT_FILE):
    print(f"Error: File not found at {INPUT_FILE}")
    exit(1)

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Top-level keys:", list(data.keys()))

    # Check for 'data' key
    if 'data' in data:
        data_content = data['data']
        print("\n'data' type:", type(data_content))
        
        if isinstance(data_content, dict):
            print("'data' keys:", list(data_content.keys()))
            
            if 'gamesFeeds' in data_content:
                games_feeds = data_content['gamesFeeds']
                print(f"\nFound 'gamesFeeds' with {len(games_feeds)} items.")
                
                if len(games_feeds) > 0:
                    first_item = games_feeds[0]
                    print("\n--- Structure of first 'gamesFeeds' item ---")
                    print("Keys:", list(first_item.keys()))
                    
                    # Try to find common nesting patterns
                    for key in first_item.keys():
                        val = first_item[key]
                        if isinstance(val, dict):
                            print(f"\n  Key '{key}' (dict) -> sub-keys: {list(val.keys())}")
                        elif isinstance(val, list):
                            print(f"\n  Key '{key}' (list) -> length: {len(val)}")
                            if len(val) > 0:
                                print(f"    First item type: {type(val[0])}")
                                if isinstance(val[0], dict):
                                    print(f"    First item keys: {list(val[0].keys())}")
                    
                    # Save a clean sample for manual inspection if needed
                    sample_file = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_structure_sample.json'
                    with open(sample_file, 'w', encoding='utf-8') as sf:
                        json.dump(first_item, sf, indent=2, ensure_ascii=False)
                    print(f"\nSample saved to: {sample_file}")
                else:
                    print("'gamesFeeds' is empty.")
            else:
                print("'gamesFeeds' not found in 'data'. Checking other keys...")
                for k, v in data_content.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        print(f"Potential list found at key: {k}")
                        print(f"  First item keys: {list(v[0].keys())}")
        else:
            print(f"'data' is not a dict, it is {type(data_content)}")
    else:
        print("'data' key not found in root.")
        print("Root keys:", list(data.keys()))

except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
except Exception as e:
    print(f"Error: {e}")
