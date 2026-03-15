#!/usr/bin/env python3
"""
Placard Sports Betting API Scraper
Scrapes sports betting data from placard.pt API (used by solverde.pt)
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# API Endpoints
INIT_URL = "https://sportswidget.placard.pt/configuration/init"
PREFETCH_URL = "https://sportswidget-cdn.placard.pt/pre-fetch"
BETSLIP_PRICES_URL = "https://sportswidget.placard.pt/betslip/prices"

# Sport IDs
SPORT_IDS = {
    "Soccer/Futsal": 5,
    "Basketball": 4942
}

class PlacardScraper:
    def __init__(self, locale="pt_PT", page="homepage", device="DESKTOP", debug=False):
        self.locale = locale
        self.page = page
        self.device = device
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })

    def log(self, message, data=None):
        if self.debug:
            print(f"[DEBUG] {datetime.now().isoformat()} - {message}")
            if data:
                print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

    def try_init(self):
        """Try to initialize session - but it's optional"""
        print("[1/4] Initializing session...")
        print(f"  URL: {INIT_URL}")

        try_methods = ["GET", "POST"]
        for method in try_methods:
            try:
                if method == "GET":
                    resp = self.session.get(INIT_URL)
                else:
                    resp = self.session.post(INIT_URL)

                if resp.status_code == 200:
                    print(f"  ✓ Init successful with {method}")
                    return resp.json()
                else:
                    print(f"  ! {method} returned {resp.status_code}")
            except Exception as e:
                print(f"  ! {method} failed: {str(e)[:80]}")

        print("  ⚠ Init failed (non-critical, continuing...)")
        return None

    def fetch_prefetch(self):
        """Fetch sports data from pre-fetch endpoint"""
        print("\n[2/4] Fetching sports data...")
        params = {
            "locale": self.locale,
            "page": self.page,
            "type": self.device
        }
        print(f"  URL: {PREFETCH_URL}")
        print(f"  Params: {params}")

        resp = self.session.get(PREFETCH_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"  ✓ Received {len(data)} top-level keys")
        return data

    def collect_event_ids(self, prefetch_data):
        """Extract event IDs from all sports and competitions"""
        print("\n[3/4] Collecting event IDs...")
        event_ids = []

        sports = prefetch_data.get("sports", [])
        print(f"  Found {len(sports)} sports")

        for sport in sports:
            sport_id = sport.get("id")
            sport_name = sport.get("name", "Unknown")
            competitions = sport.get("competitions", [])

            for comp in competitions:
                comp_id = comp.get("id")
                comp_name = comp.get("name", "Unknown")
                events = comp.get("events", [])

                for event in events:
                    if isinstance(event, dict):
                        event_id = event.get("id")
                        if event_id:
                            event_ids.append({
                                "event_id": event_id,
                                "event_name": event.get("name", "Unknown"),
                                "sport_id": sport_id,
                                "sport_name": sport_name,
                                "competition_id": comp_id,
                                "competition_name": comp_name
                            })

        print(f"  ✓ Collected {len(event_ids)} unique events")
        self.log(f"Sample event IDs: {event_ids[:3]}")
        return event_ids

    def fetch_prices(self, event_ids):
        """Fetch prices/odds for collected events"""
        print("\n[4/4] Fetching betting prices...")
        print(f"  URL: {BETSLIP_PRICES_URL}")

        if not event_ids:
            print("  ⚠ No events to fetch prices for")
            return []

        # Batch event IDs (API may have limits)
        all_event_ids = [e["event_id"] for e in event_ids]
        batch_size = 50
        prices_data = []

        for i in range(0, len(all_event_ids), batch_size):
            batch = all_event_ids[i:i+batch_size]
            try:
                payload = {"eventIds": batch}
                resp = self.session.post(
                    BETSLIP_PRICES_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list):
                    prices_data.extend(data)
                elif isinstance(data, dict) and "prices" in data:
                    prices_data.extend(data["prices"])
                print(f"  ✓ Fetched prices for batch {i//batch_size + 1} ({len(batch)} events)")
            except Exception as e:
                print(f"  ! Failed batch {i//batch_size + 1}: {str(e)[:80]}")

        print(f"  ✓ Total prices received: {len(prices_data)}")
        return prices_data

    def process_data(self, prefetch_data, prices_data, event_ids):
        """Combine pre-fetch and prices data into structured output"""
        print("\n[5/4] Processing and structuring data...")

        # Build odds lookup map
        odds_map = {}
        for price in prices_data:
            if isinstance(price, dict):
                event_id = price.get("eventId") or price.get("event_id")
                if event_id:
                    odds_map[event_id] = price

        # Merge event info with odds
        processed_events = []
        for event_info in event_ids:
            event_id = event_info["event_id"]
            event_data = {
                "id": event_id,
                "name": event_info["event_name"],
                "sport": {
                    "id": event_info["sport_id"],
                    "name": event_info["sport_name"]
                },
                "competition": {
                    "id": event_info["competition_id"],
                    "name": event_info["competition_name"]
                },
                "odds": odds_map.get(event_id, {})
            }
            processed_events.append(event_data)

        # Build output structure
        output = {
            "metadata": {
                "scraper": "placard_scraper",
                "scraped_at": datetime.now().isoformat(),
                "locale": self.locale,
                "total_events": len(processed_events),
                "events_with_odds": len([e for e in processed_events if e["odds"]])
            },
            "data": {
                "prefetch": prefetch_data.get("sports", []),
                "events": processed_events
            }
        }

        return output

    def scrape(self, output_file="placard_data.json"):
        """Main scraping workflow"""
        print("="*60)
        print("Placard Sports Betting Scraper")
        print("="*60)
        print(f"Start time: {datetime.now().isoformat()}")
        print()

        try:
            # Step 1: Initialize (optional)
            init_data = self.try_init()

            # Step 2: Fetch pre-fetch data
            prefetch_data = self.fetch_prefetch()

            # Step 3: Collect event IDs
            event_ids = self.collect_event_ids(prefetch_data)

            # Step 4: Fetch prices
            prices_data = self.fetch_prices(event_ids)

            # Step 5: Process and save
            output = self.process_data(prefetch_data, prices_data, event_ids)

            print(f"\n[6/4] Saving to {output_file}...")
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Saved {output_path.stat().st_size} bytes")

            # Save intermediate files
            print(f"  ✓ Saving intermediate responses...")
            if init_data:
                with open("placard_init_response.json", 'w') as f:
                    json.dump(init_data, f, indent=2)
            with open("placard_prefetch_response.json", 'w') as f:
                json.dump(prefetch_data, f, indent=2)

            if prices_data:
                with open("placard_prices_response.json", 'w') as f:
                    json.dump(prices_data, f, indent=2)

            print(f"\n{'='*60}")
            print(f"Scraping completed successfully!")
            print(f"{'='*60}")
            print(f"Events collected: {output['metadata']['total_events']}")
            print(f"Events with odds: {output['metadata']['events_with_odds']}")
            print(f"Files created:")
            print(f"  - {output_file}")
            print(f"  - placard_prefetch_response.json")
            print(f"  - placard_prices_response.json")
            if init_data:
                print(f"  - placard_init_response.json")

            return True

        except Exception as e:
            print(f"\n[FAILED] {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    debug = "--debug" in sys.argv
    output = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "placard_data.json"

    scraper = PlacardScraper(debug=debug)
    success = scraper.scrape(output_file=output)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
