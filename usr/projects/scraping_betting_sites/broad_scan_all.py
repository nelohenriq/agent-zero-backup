import json
import os
from pathlib import Path

def deep_search(obj, path="", found=None, keywords=None):
 if found is None:
 found = []
 if keywords is None:
 keywords = {"match", "team", "odds", "fixture", "home", "away", "sport", "competition", "market", "selection", "outcome", "score", "date", "time"}
 
 if isinstance(obj, dict):
 keys = set(obj.keys())
 if keys & keywords:
 found.append((path, list(keys & keywords), obj))
 for k, v in obj.items():
 deep_search(v, f"{path}.{k}", found, keywords)
 elif isinstance(obj, list):
 for i, item in enumerate(obj):
 deep_search(item, f"{path}[{i}]", found, keywords)
 return found

processed_dir = Path("/a0/usr/projects/scraping_betting_sites/processed_sports")
all_files = list(processed_dir.glob("*.json"))

print(f"Scanning {len(all_files)} JSON files...")

results = []
for file_path in all_files:
 try:
 with open(file_path, "r", encoding="utf-8") as f:
 content = f.read()
 
 # Try to parse as JSON
 try:
 data = json.loads(content)
 except json.JSONDecodeError:
 continue
 
 # Check for string bodies that might be JSON
 if isinstance(data, list):
 for i, item in enumerate(data):
 if isinstance(item, dict):
 for key in ["full_body", "body", "response", "payload"]:
 if key in item and isinstance(item[key], str):
 try:
 inner_data = json.loads(item[key])
 matches = deep_search(inner_data)
 if matches:
 results.append((str(file_path), f"Item {i}.{key}", matches))
 except:
 pass
 
 # Deep search the main structure
 matches = deep_search(data)
 if matches:
 results.append((str(file_path), "root", matches))
 
 except Exception as e:
 print(f"Error reading {file_path}: {e}")

print(f"\nFound {len(results)} files with potential sports data.")
for file_path, location, matches in results:
 print(f"\n--- File: {Path(file_path).name} ---")
 print(f"Location: {location}")
 print(f"Matches found: {len(matches)}")
 for path, keys, obj in matches[:3]: # Show top 3
 print(f"  Path: {path}")
 print(f"  Keys: {keys}")
 print(f"  Snippet: {json.dumps(obj, indent=2)[:200]}...")

