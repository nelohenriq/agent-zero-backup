import asyncio
import json
import time
import os
from playwright.async_api import async_playwright

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports/json_backup"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        
        print("Navigating to Solverde sports page...")
        await page.goto("https://www.solverde.pt/pt-pt/apostas-desportivas", wait_until="networkidle", timeout=60000)
        
        print("Waiting for match cards to load...")
        try:
            await page.wait_for_selector(".ta-MatchEventCard", timeout=15000)
        except:
            print("Match cards not found. Trying alternative selectors...")
            await page.wait_for_selector(".ta-headerTitle", timeout=15000)
        
        print("Extracting match data from DOM...")
        matches = await page.evaluate("""
            () => {
                const cards = document.querySelectorAll(".ta-MatchEventCard");
                const data = [];
                cards.forEach(card => {
                    const league = card.querySelector(".ta-headerTitle");
                    const team = card.querySelector(".ta-participantName");
                    const market = card.querySelector(".ta-SelectionButtonView .ta-infoTextName");
                    const price = card.querySelector(".ta-SelectionButtonView .ta-price_text");
                    const period = card.querySelector(".ta-MatchEventCard_period");
                    
                    if (team) {
                        data.push({
                            league: league ? league.innerText.trim() : "Unknown",
                            match: team.innerText.trim(),
                            market: market ? market.innerText.trim() : "N/A",
                            odds: price ? price.innerText.trim() : "N/A",
                            period: period ? period.innerText.trim() : "N/A"
                        });
                    }
                });
                return data;
            }
        """)
        
        print(f"Found {len(matches)} matches.")
        if matches:
            filename = f"solverde_dom_extract_{int(time.time())}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"timestamp": time.time(), "matches": matches}, f, indent=2, ensure_ascii=False)
            print(f"[SAVED] {filename}")
        else:
            print("No matches found. Saving full HTML for inspection...")
            html = await page.content()
            filename = f"solverde_full_html_{int(time.time())}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"html": html}, f, indent=2, ensure_ascii=False)
            print(f"[SAVED] {filename} (full HTML)")
        
        await browser.close()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
