import requests
import json

HEADERS = {
    "Origin": "https://www.placard.pt",
    "Referer": "https://www.placard.pt/",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

BASE_URL = "https://sportswidget.placard.pt/api"

def check_endpoint(path):
    url = f"{BASE_URL}{path}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            print(f"[SUCCESS] {url}")
            return r.json()
        else:
            print(f"[FAIL] {url} - {r.status_code}")
    except Exception as e:
        print(f"[ERROR] {url} - {e}")
    return None

# 1. Check Sport Menu to find IDs
menu = check_endpoint("/sportmenu/gmt?locale=pt")
if menu:
    # Search for soccer and its event groups
    # The menu structure is usually hierarchical
    def search_soccer(item):
        if isinstance(item, dict):
            if item.get('id') == 'soccer':
                print("Found Soccer in menu:")
                print(json.dumps(item, indent=2)[:1000])
            for v in item.values():
                search_soccer(v)
        elif isinstance(item, list):
            for i in item:
                search_soccer(i)
    search_soccer(menu)

# 2. Try common variations if menu doesn't help
check_endpoint("/eventgroups/soccer-popular-match-events?locale=pt")
check_endpoint("/eventgroups/soccer-today-match-events?locale=pt")
