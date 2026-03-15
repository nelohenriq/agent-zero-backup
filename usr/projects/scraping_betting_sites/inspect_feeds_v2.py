import json
import os

INPUT_FILE = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_raw_debug.json'

if not os.path.exists(INPUT_FILE):
 print(f"Error: File not found at {INPUT_FILE}")
 exit(1)

try:
 with open(INPUT_FILE, 'r', encoding='utf-8') as f:
 data = json.load(f)

 print(f"Root type: {type(data)}")

 # Handle list root
 if isinstance(data, list):
 print(f"Root is a list with {len(data)} items.")
 if len(data) > 0:
 first_item = data[0]
 print("\n--- Structure of first item in root list ---")
 print("Keys:", list(first_item.keys()) if isinstance(first_item, dict) else "Not a dict")
 
 if isinstance(first_item, dict):
 # Check for 'data' key inside the item
 if 'data' in first_item:
 inner_data = first_item['data']
 print(f"\nFound 'data' key. Type: {type(inner_data)}")
 if isinstance(inner_data, dict):
 print("'data' keys:", list(inner_data.keys()))
 if 'gamesFeeds' in inner_data:
 feeds = inner_data['gamesFeeds']
 print(f"\nFound 'gamesFeeds' with {len(feeds)} items.")
 if len(feeds) > 0:
 sample_feed = feeds[0]
 print("\n--- Structure of first 'gamesFeeds' item ---")
 print("Keys:", list(sample_feed.keys()))
 
 # Save sample for detailed review
 sample_file = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_structure_sample_v2.json'
 with open(sample_file, 'w', encoding='utf-8') as sf:
 json.dump(sample_feed, sf, indent=2, ensure_ascii=False)
 print(f"\nSample saved to: {sample_file}")
 
 # Look for country/competition/match keys
 for key in sample_feed.keys():
 val = sample_feed[key]
 if isinstance(val, dict):
 print(f"\n Key '{key}' (dict) -> sub-keys: {list(val.keys())}")
 elif isinstance(val, list):
 print(f"\n Key '{key}' (list) -> length: {len(val)}")
 if len(val) > 0 and isinstance(val[0], dict):
 print(f" First item keys: {list(val[0].keys())}")
 else:
 print(f"\n'gamesFeeds' is empty.")
 else:
 print("\n'gamesFeeds' not found in 'data'.")
 print("Available keys in 'data':", list(inner_data.keys()))
 else:
 print("\n'data' key not found in first item.")
 print("Available keys in first item:", list(first_item.keys()))
 else:
 print("First item is not a dict.")
 else:
 print("Root list is empty.")
 
 # Fallback: Check if root dict has 'data' directly (if previous assumption was partially right but wrapped)
elif isinstance(data, dict):
 if 'data' in data:
 inner = data['data']
 if isinstance(inner, list):
 print(f"\n'data' is a list with {len(inner)} items.")
 if len(inner) > 0:
 first = inner[0]
 if isinstance(first, dict):
 print("First 'data' item keys:", list(first.keys()))
 if 'gamesFeeds' in first:
 feeds = first['gamesFeeds']
 print(f"Found 'gamesFeeds' with {len(feeds)} items.")
 if len(feeds) > 0:
 sample = feeds[0]
 print("Sample keys:", list(sample.keys()))
 sample_file = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_structure_sample_v2.json'
 with open(sample_file, 'w', encoding='utf-8') as sf:
 json.dump(sample, sf, indent=2, ensure_ascii=False)
 print(f"Sample saved to: {sample_file}")

except json.JSONDecodeError as e:
 print(f"JSON Decode Error: {e}")
except Exception as e:
 print(f"Error: {e}")
