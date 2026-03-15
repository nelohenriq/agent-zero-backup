import requests
import json

HEADERS = {
    "Origin": "https://www.placard.pt",
    "Referer": "https://www.placard.pt/",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

BASE_URL = "https://sportswidget.placard.pt/api"

def main():
    # Try to fetch the sport menu which contains all categories and eventgroup IDs
    url = f"{BASE_URL}/sportmenu/gmt?locale=pt"
    print(f"Fetching menu from: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Search for soccer and its subgroups
            def find_soccer_groups(items):
                for item in items:
                    if item.get('id') == 'soccer':
                        print("Found Soccer Category. Subgroups:")
                        for child in item.get('children', []):
                            print(f"  - Name: {child.get('name')}, ID: {child.get('id')}, Type: {child.get('type')}")
                            if 'children' in child:
                                for subchild in child['children']:
                                    print(f"    * Sub-Name: {subchild.get('name')}, ID: {subchild.get('id')}")
                    if 'children' in item:
                        find_soccer_groups(item['children'])

            find_soccer_groups(data.get('menuItems', []))
        else:
            print(f"Failed to fetch menu: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
