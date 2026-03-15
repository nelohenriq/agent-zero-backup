import json
import os
from pathlib import Path

data_dir = Path("/a0/usr/projects/scraping_betting_sites/processed_sports")

# Common sports keys to look for
sports_keys = {
 "match", "fixture", "event", "team", "league", "competition", 
 "odds", "home", "away", "score", "period", "status", "sportId",
 "homeTeam", "awayTeam", "homeScore", "awayScore", "markets", "selections",
 "events", "fixtures", "competitions", "sport", "leagueId", "eventId",
 "id", "name", "startTimestamp", "slug", "tournament", "category"
}

def deep_check(obj, depth=0, path="root"):
 """Recursively check for sports keys and return path if found."""
 if depth > 5:
 return None
 if isinstance(obj, dict):
 for k, v in obj.items():
 if k.lower() in sports_keys:
 return path + "/" + k
 if isinstance(v, (dict, list)):
 res = deep_check(v, depth+1, path+"/"+k)
 if res:
 return res
 elif isinstance(obj, list):
 for i, item in enumerate(obj):
 if isinstance(item, (dict, list)):
 res = deep_check(item, depth+1, path+"/"+str(i))
 if res:
 return res
 return None

print("Performing broad scan of all JSON files...\n")
found_files = []

for filepath in data_dir.glob("*.json"):
 try:
 with open(filepath, 'r', encoding='utf-8') as f:
 data = json.load(f)
 
 match_path = deep_check(data)
 if match_path:
 found_files.append((filepath.name, match_path))
 print(f"[FOUND] {filepath.name} -> {match_path}")
 except json.JSONDecodeError:
 pass
 except Exception as e:
 pass

if found_files:
 print(f"\n=== {len(found_files)} files with potential sports data found ===")
 # Sort by name
 found_files.sort(key=lambda x: x[0])
 for fname, path in found_files:
 print(f" - {fname}: {path}")
 
 # Show snippet of the first match
 first_file = Path(data_dir) / found_files[0][0]
 with open(first_file, 'r', encoding='utf-8') as f:
 data = json.load(f)
 print(f"\n--- Snippet from {found_files[0][0]} ---")
 # Try to print the first 500 chars of the file content
 with open(first_file, 'r', encoding='utf-8') as f:
 content = f.read()
 print(content[:1000])
else:
 print("\nNo files with sports keys found. The data might be encrypted, base64, or in a non-JSON format.")
 print("I will now list all files and their sizes to investigate further.")
 for f in data_dir.glob("*.json"):
 print(f"{f.name}: {f.stat().st_size} bytes")
