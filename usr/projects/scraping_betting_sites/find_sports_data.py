import json
import os
from pathlib import Path

data_dir = Path("/a0/usr/projects/scraping_betting_sites/processed_sports")
sports_keywords = [
 "match", "fixture", "event", "team", "league", "competition", 
 "odds", "home", "away", "score", "period", "status", "sportId",
 "homeTeam", "awayTeam", "homeScore", "awayScore", "markets", "selections",
 "events", "fixtures", "competitions", "sport", "leagueId", "eventId"
]

def is_sports_data(json_obj, depth=0):
    if depth > 6:
        return False, []
    found_keywords = []
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key.lower() in [k.lower() for k in sports_keywords]:
                found_keywords.append(key)
            if isinstance(value, (dict, list)):
                sub_found, _ = is_sports_data(value, depth + 1)
                found_keywords.extend(sub_found)
    elif isinstance(json_obj, list):
        for item in json_obj:
            if isinstance(item, (dict, list)):
                sub_found, _ = is_sports_data(item, depth + 1)
                found_keywords.extend(sub_found)
    return len(found_keywords) > 1, list(set(found_keywords))

def analyze_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        has_data, keywords = is_sports_data(data)
        if has_data:
            return data, keywords
    except Exception as e:
        return None, str(e)
    return None, []

files_to_check = [
    "solverde_match_data_filtered_20260307_004845.json",
    "solverde_api_intercept_fixed_20260307_004801.json",
    "solverde_api_intercept_20260307_004713.json",
    "solverde_futebol_intercepted_v2.json",
    "solverde_deep_scan_20260307_002912.json",
    "solverde_final_capture.json",
    "solverde_ws_grpc_dump.json"
]

print("Scanning files for hidden sports data...\n")
best_match = None
best_score = 0
best_file = None

for filename in files_to_check:
    filepath = data_dir / filename
    if not filepath.exists():
        continue
    print(f"Checking {filename}...")
    data, keywords = analyze_file(filepath)
    if data:
        score = len(keywords)
        print(f" -> FOUND SPORTS DATA! Keywords: {keywords}")
        if score > best_score:
            best_score = score
            best_match = data
            best_file = filename
    else:
        print(f" -> No significant sports data found.")

if best_match:
    print(f"\n=== BEST MATCH FOUND ===")
    print(f"File: {best_file}")
    print(f"Total keywords found: {best_score}")
    output_path = data_dir / "best_sports_payload_found.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(best_match, f, indent=2, ensure_ascii=False)
    print(f"Saved full payload to: {output_path}")
    if isinstance(best_match, dict):
        for key in ["events", "matches", "fixtures", "data", "sports", "competitions", "eventsList", "odds"]:
            if key in best_match:
                print(f"\nSample structure under '{key}':")
                sample = best_match[key]
                if isinstance(sample, list) and len(sample) > 0:
                    print(json.dumps(sample[0], indent=2, ensure_ascii=False)[:1500])
                else:
                    print(json.dumps(sample, indent=2, ensure_ascii=False)[:1500])
                break
        else:
            print("\nNo standard keys found, printing top-level keys:")
            print(list(best_match.keys())[:20])
else:
    print("\nNo valid sports data found in the scanned files.")
