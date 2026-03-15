import asyncio
import json
import os
from toon_utils import json_to_toon
from datetime import datetime
from playwright.async_api import async_playwright

async def run_deep_scraper():
    output_file = "/a0/usr/projects/scraping_betting_sites/placard_deep_data.json"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("--- PLACARD MULTI-SPORT DEEP SCRAPER (SOCCER & NBA) ---")
        print("Loading match schedules from Placard.pt...")

        homepage_prefetch = "https://sportswidget-cdn.placard.pt/pre-fetch?locale=pt_PT&page=homepage&type=DESKTOP"

        try:
            await page.goto("https://www.placard.pt/", wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Initial navigation failed: {e}. Trying fetch anyway...")

        # 1. Get Global Match List
        try:
            data = await page.evaluate("""
                async (url) => {
                    const resp = await fetch(url);
                    if (!resp.ok) throw new Error('HTTP ' + resp.status);
                    return await resp.json();
                }
            """, homepage_prefetch)
        except Exception as e:
            print(f"Failed to fetch homepage data: {e}")
            await browser.close()
            return

        events = data.get('events', [])
        if not events:
             for eg in data.get('eventGroups', []):
                 for group in eg.get('groups', []):
                     events.extend(group.get('events', []))

        # Filter for Soccer and NBA (Basketball)
        target_matches = []
        for e in events:
            sport_id = e.get('sportId')
            type_name = e.get('typeName', '')
            if sport_id == 'soccer' or (sport_id == 'basketball' and 'NBA' in type_name.upper()):
                target_matches.append(e)

        captured_data = []

        if not target_matches:
            print("No Soccer or NBA matches found.")
        else:
            print(f"Found {len(target_matches)} target matches (Soccer & NBA). Performing deep dive...\n")
            
            for match in target_matches:
                mid = match.get('id')
                name = match.get('name', 'Unknown')
                sport = match.get('sportId', 'unknown').upper()
                print(f"DEEP DIVE [{sport}]: {name} (ID: {mid})")

                # 2. Fetch Event-Specific Pre-fetch for ALL Markets (with retry)
                event_url = f"https://sportswidget-cdn.placard.pt/pre-fetch?locale=pt_PT&page=event&eventId={mid}&type=DESKTOP"
                
                event_data = None
                for attempt in range(3):
                    try:
                        event_data = await page.evaluate("""
                            async (url) => {
                                const resp = await fetch(url);
                                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                                return await resp.json();
                            }
                        """, event_url)
                        break
                    except Exception as e:
                        if attempt == 2:
                            print(f"    [!] Final attempt failed for {mid}: {e}")
                        else:
                            await asyncio.sleep(1)

                if not event_data:
                    continue

                full_markets = event_data.get('markets', [])
                match_entry = {
                    "match_id": mid,
                    "name": name,
                    "sport": sport,
                    "type": match.get('typeName', 'N/A'),
                    "start_time": match.get('startTime', 'N/A'),
                    "market_count": len(full_markets),
                    "markets": []
                }

                for market in full_markets:
                    market_entry = {
                        "market_name": market.get('name', 'Market'),
                        "selections": []
                    }
                    for s in market.get('selections', []):
                        price = "N/A"
                        if s.get('prices'):
                            price = s['prices'][0].get('decimalLabel', 'N/A')
                        market_entry["selections"].append({
                            "name": s.get('name', 'Selection'),
                            "odds": price
                        })
                    match_entry["markets"].append(market_entry)

                captured_data.append(match_entry)
                print(f"    ✅ Captured {len(full_markets)} markets.")

        # 3. Save to JSON
        final_output = {
            "timestamp": datetime.now().isoformat(),
            "matches": captured_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(final_output, f, indent=4)
            
        print(f"\nScraping complete. Data saved to: {output_file}")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_deep_scraper())
