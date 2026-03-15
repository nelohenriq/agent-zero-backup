
import json
import os
from pathlib import Path

data_dir = Path("/a0/usr/projects/scraping_betting_sites/processed_sports")

sports_keys = {
    "match", "fixture", "event", "team", "league", "competition",
    "odds", "home", "away", "score", "period", "status", "sportId",
    "homeTeam", "awayTeam", "homeScore", "awayScore", "markets", "selections",
    "events", "fixtures", "competitions", "sport", "leagueId", "eventId",
    "id", "name", "startTimestamp", "slug", "tournament", "category",
    "winner", "draw", "total", "handicap", "line", "price", "decimal",
    "outcomes", "odds", "bookmaker", "selections",
    "fixtureId", "matchId", "eventId", "sportId", "leagueId"
}

def deep_check(obj, depth=0, path="root"):
    if depth > 6:
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

for filepath in sorted(data_dir.glob("*.json")):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                continue
            data = json.loads(content)
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
    found_files.sort(key=lambda x: x[0])
    for fname, path in found_files:
        print(f" - {fname}: {path}")

    first_file = Path(data_dir) / found_files[0][0]
    with open(first_file, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"\n--- Snippet from {found_files[0][0]} (first 1000 chars) ---")
    print(content[:1000])
else:
    print("\nNo files with sports keys found.")
    print("Listing all files and their sizes:")
    for f in sorted(data_dir.glob("*.json")):
        size = f.stat().st_size
        print(f"{f.name}: {size} bytes")
