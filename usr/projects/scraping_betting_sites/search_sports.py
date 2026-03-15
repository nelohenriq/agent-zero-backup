import json
import glob

print("=== Searching for sports/football data in captures ===\n")

files = glob.glob("processed_sports/*.json")
sports_keywords = ['futebol', 'football', 'soccer', 'liga', 'odd', 'aposta', 'match']

sports_found = []

for fpath in files:
    try:
        with open(fpath) as f:
            content = f.read()
        fname = fpath.split('/')[-1]
        if any(k in content.lower() for k in sports_keywords):
            sports_found.append(fname)
    except:
        pass

print(f"Files with sports keywords: {len(sports_found)}")
for f in sports_found[:10]:
    print(f"  - {f}")

# Check solverde_api_capture_full for sports
print("\n=== Checking for SPORTS endpoints in full capture ===")
try:
    with open("processed_sports/solverde_api_capture_full_20260307_001048.json") as f:
        data = json.load(f)
    for resp in data:
        url = resp.get("url", "")
        if "sport" in url.lower() or "futebol" in url.lower():
            print(f"Found: {url}")
except Exception as e:
    print(f"Error: {e}")

