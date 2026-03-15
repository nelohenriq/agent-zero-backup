import json
import os
import glob

# Keywords to identify betting data
keywords = ['odds', 'selection', 'team', 'participant', 'match', 'event', 'league', 'sport', 'fixture', 'home', 'away', 'score', 'price', 'win', 'draw', 'lose']

# Directory to scan
dir_path = '/a0/usr/projects/scraping_betting_sites/processed_sports/json_backup'
files = glob.glob(os.path.join(dir_path, '*.json'))

print(f"Scanning {len(files)} files in {dir_path}...\n")

found_files = []

for file_path in files:
 try:
 with open(file_path, 'r', encoding='utf-8') as f:
 # Try to load as JSON
 try:
 data = json.load(f)
 except json.JSONDecodeError:
 continue # Skip invalid JSON

 # Recursive search for keywords
 def find_matches(obj, path=""):
 matches = []
 if isinstance(obj, dict):
 for k, v in obj.items():
 current_path = f"{path}.{k}" if path else k
 if any(kw in k.lower() for kw in keywords):
 matches.append((current_path, str(v)[:100]))
 matches.extend(find_matches(v, current_path))
 elif isinstance(obj, list):
 for i, item in enumerate(obj):
 current_path = f"{path}[{i}]"
 matches.extend(find_matches(item, current_path))
 return matches

 matches = find_matches(data)
 if matches:
 found_files.append((file_path, matches))
 print(f"[FOUND] {os.path.basename(file_path)}: {len(matches)} matches")
 for path, snippet in matches[:3]: # Show first 3 matches
 print(f"  -> {path}: {snippet}...")

 except Exception as e:
 print(f"[ERROR] {file_path}: {e}")

print(f"\nTotal files with betting data: {len(found_files)}")
if found_files:
 print("\nRecommendation: Focus on these files for data extraction.")
