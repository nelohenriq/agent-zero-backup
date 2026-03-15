import asyncio
import json
import os
from toon_utils import json_to_toon
from datetime import datetime
from playwright.async_api import async_playwright

async def run_futsal_scraper():
    output_file = "/a0/usr/projects/scraping_betting_sites/futsal_data.json"
    list_url = "https://www.placard.pt/apostas/sports/futsal/matches/48h"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("--- PLACARD FUTSAL HIERARCHICAL SCRAPER ---")
        print(f"Navigating to {list_url} to discover matches...")

        try:
            await page.goto(list_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Discovery failed: {e}")
            await browser.close()
            return

        # Discovery logic: Extract all futsal event IDs from links
        # We use a simple loop and querySelectorAll to be safe from SyntaxErrors
        match_ids = await page.evaluate("""() => {
            const ids = [];
            const anchors = Array.from(document.querySelectorAll('a'));
            for (const a of anchors) {
                const href = a.getAttribute('href') || '';
                const m = href.match(/\\/futsal\\/events\\/(\\d+)/);
                if (m && m[1]) {
                    if (!ids.includes(m[1])) ids.push(m[1]);
                }
            }
            return ids;
        }""")

        structured_results = {}

        if not match_ids:
            print("No Futsal matches discovered.")
        else:
            print(f"Discovered {len(match_ids)} Futsal matches. Starting deep extraction...\n")

            for mid in match_ids:
                event_url = f"https://www.placard.pt/apostas/sports/futsal/events/{mid}"
                print(f"Deep dive: {event_url}")

                try:
                    await page.goto(event_url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(3)

                    # Extract Data from window.__INITIAL_STATE__
                    # We extract the entire prefetch and then find the right one
                    state = await page.evaluate("() => window.__INITIAL_STATE__")

                    if not state or 'prefetch' not in state:
                        print(f"    [!] No state found for {mid}")
                        continue

                    # Find the specific prefetch object containing markets for this match
                    event_data = None
                    for val in state['prefetch'].values():
                        if isinstance(val, dict) and 'markets' in val and len(val['markets']) > 0:
                             # Confirm it's the right match by checking events in that prefetch block
                             if any(str(e.get('id')) == str(mid) for e in val.get('events', [])):
                                 event_data = val
                                 break

                    if not event_data:
                        print(f"    [!] Market data not found in state for {mid}")
                        continue

                    # Extract Match Info
                    target_event = next(e for e in event_data['events'] if str(e.get('id')) == str(mid))
                    name = target_event.get('name', 'Unknown')
                    country = target_event.get('className', 'Unknown')
                    competition = target_event.get('typeName', 'Other')

                    match_entry = {
                        "match_id": mid,
                        "name": name,
                        "start_time": target_event.get('startTime', 'N/A'),
                        "market_count": len(event_data['markets']),
                        "markets": []
                    }

                    for market in event_data['markets']:
                        m_entry = {
                            "market_id": market.get('id'),
                            "market_name": market.get('name'),
                            "selections": []
                        }
                        for s in market.get('selections', []):
                            price = s['prices'][0].get('decimalLabel', 'N/A') if s.get('prices') else 'N/A'
                            m_entry["selections"].append({"name": s.get('name'), "odds": price})
                        match_entry["markets"].append(m_entry)

                    # Organize into hierarchy
                    if country not in structured_results: structured_results[country] = {}
                    if competition not in structured_results[country]: structured_results[country][competition] = []
                    structured_results[country][competition].append(match_entry)
                    print(f"    ✅ Captured {len(event_data['markets'])} markets in {country} | {competition}")

                except Exception as e:
                    print(f"    [!] Error processing {mid}: {e}")

        # Save Final Output
        final_output = {
            "sport": "FUTSAL",
            "timestamp": datetime.now().isoformat(),
            "countries": structured_results
        }

        with open(output_file, 'w') as f:
            json.dump(final_output, f, indent=4)

        
        # Save TOON Output
        toon_file = output_file.replace('.json', '.toon')
        with open(toon_file, 'w') as f:
            f.write(json_to_toon(final_output))
        print(f"TOON version saved to: {toon_file}")

        print(f"\nScraping complete. Results saved to: {output_file}")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_futsal_scraper())
