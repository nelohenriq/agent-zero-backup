import json

# Check live data structure
print("=== Checking solverde_live_captured_data.json ===")
with open("processed_sports/solverde_live_captured_data.json") as f:
    live_data = json.load(f)
print(f"Type: {type(live_data)}, Length: {len(live_data)}")
if live_data:
    print(f"First item type: {type(live_data[0])}")
    print(f"First item keys: {live_data[0].keys() if isinstance(live_data[0], dict) else live_data[0]}")

# Explore the games feeds more deeply
print("\n=== Exploring gamesFeeds in initialResources ===")
with open("processed_sports/solverde_api_capture_full_20260307_001048.json") as f:
    data = json.load(f)

for resp in data:
    url = resp.get("url", "")
    if "initialResources" in url and "games" in url:
        body = resp.get("data", {})
        feeds = body.get("gamesFeeds", [])
        print(f"Found {len(feeds)} game feeds:")
        for feed in feeds[:10]:
            print(f" - {feed.get('name', 'UNNAMED')}")
            categories = feed.get("categories", [])
            if categories:
                print(f"   Categories: {len(categories)}, first: {categories[0].get('name', '?')}")

