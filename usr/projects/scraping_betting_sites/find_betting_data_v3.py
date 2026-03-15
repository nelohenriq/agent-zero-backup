import json
from pathlib import Path

def find_betting_data(obj, path="", results=None):
    if results is None:
        results = []
    target_keys = {"odds", "markets", "fixture", "homeTeam", "awayTeam", "sportId", "competitionId", "matchId", "selections", "outcomes"}
    
    if isinstance(obj, dict):
        keys = set(obj.keys())
        if keys & target_keys:
            results.append((path, obj))
        for k, v in obj.items():
            find_betting_data(v, f"{path}.{k}", results)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_betting_data(item, f"{path}[{i}]", results)
    return results

file_path = "/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_api_intercept_fixed_20260307_004801.json"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Scanning {file_path}...")
    print(f"Root is list with {len(data)} items.")
    
    total_matches = 0
    for i, item in enumerate(data):
        if "full_body" in item:
            content = item["full_body"]
            if isinstance(content, str):
                try:
                    parsed = json.loads(content)
                    matches = find_betting_data(parsed)
                    if matches:
                        print(f"\n[Item {i}] Found {len(matches)} betting data objects!")
                        for path, obj in matches:
                            print(f" Path: {path}")
                            print(f" Keys: {list(obj.keys())}")
                            snippet = json.dumps(obj, indent=2)[:500]
                            print(f" Snippet: {snippet}...")
                        total_matches += len(matches)
                        if total_matches > 5:
                            print("... (truncated)")
                            break
                except json.JSONDecodeError:
                    pass
    print(f"\nTotal betting data objects found: {total_matches}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
