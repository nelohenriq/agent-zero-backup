import json
import requests

def get_nba_matches():
    url = "https://sportswidget-cdn.placard.pt/pre-fetch?locale=pt_PT&type=DESKTOP"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"Error fetching data: {e}"

    events = data.get('events', [])
    nba_matches = []

    for event in events:
        if event.get('sportId') == 'basketball' and event.get('typeName') == 'NBA':
            match_info = {
                'id': event.get('id'),
                'name': event.get('name'),
                'startTime': event.get('startTime'),
                'marketCount': event.get('numberOfMarkets'),
                'prefetch_url': f"https://sportswidget-cdn.placard.pt/pre-fetch?locale=pt_PT&page=event&eventId={event.get('id')}&type=DESKTOP"
            }
            nba_matches.append(match_info)

    return nba_matches

if __name__ == "__main__":
    matches = get_nba_matches()
    if isinstance(matches, str):
        print(matches)
    else:
        print(f"Found {len(matches)} NBA matches.")
        header = f"{'ID':<15} | {'Match Name':<40} | {'Markets':<8} | {'Start Time'}"
        print(header)
        print("-" * len(header))
        for m in matches:
            print(f"{m['id']:<15} | {m['name']:<40} | {m['marketCount']:<8} | {m['startTime']}")

        if matches:
            print(f"\nExample Detail Pre-fetch URL: {matches[0]['prefetch_url']}")