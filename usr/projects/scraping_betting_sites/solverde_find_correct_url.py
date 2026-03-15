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

        print("Navigating to Solverde homepage...")
        await page.goto("https://www.solverde.pt", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        # 1. Handle Cookie Consent
        print("Accepting cookies...")
        try:
            btn = await page.wait_for_selector(".EuAceitoBtn", timeout=5000)
            if btn:
                await btn.click(force=True)
                await asyncio.sleep(2)
        except Exception as e:
            print(f"Cookie button not found: {e}")

        # 2. Find 'APOSTAS DESPORTIVAS' link
        print("Looking for 'APOSTAS DESPORTIVAS' link...")
        sports_link = None
        try:
            # Try to find the link by text content
            sports_link = await page.wait_for_selector("//a[contains(text(), 'APOSTAS DESPORTIVAS') or contains(text(), 'Apostas Desportivas')]", timeout=10000)
        except Exception:
            pass

        if sports_link:
            sports_url = await sports_link.get_attribute("href")
            print(f"Found URL: {sports_url}")

            # 3. Navigate to the correct URL
            print("Navigating to sports page...")
            if not sports_url.startswith("http"):
                sports_url = f"https://www.solverde.pt{sports_url}"

            await page.goto(sports_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)

            # 4. Wait for content
            print("Waiting for sports content...")
            try:
                await page.wait_for_selector(".ta-headerTitle", timeout=15000)
                print("Sports content detected!")
            except Exception as e:
                print(f"Sports content not found: {e}")
                await asyncio.sleep(5)

            # 5. Save HTML and Screenshot
            html = await page.content()
            ts = int(time.time())
            with open(os.path.join(OUTPUT_DIR, f"solverde_correct_url_html_{ts}.html"), "w", encoding="utf-8") as f:
                f.write(html)
            await page.screenshot(path=os.path.join(OUTPUT_DIR, f"solverde_correct_url_screenshot_{ts}.png"), full_page=True)
            print(f"[SAVED] HTML and Screenshot")

            # 6. Extract Data
            try:
                data = await page.evaluate("""
                () => {
                    const results = [];
                    const matches = document.querySelectorAll(".ta-MatchEventCard");
                    matches.forEach(match => {
                        const header = match.querySelector(".ta-headerTitle");
                        const teams = match.querySelectorAll(".ta-participantName");
                        const oddsBtns = match.querySelectorAll(".ta-SelectionButtonView");
                        const matchData = {
                            league: header ? header.textContent.trim() : "Unknown",
                            teams: Array.from(teams).map(t => t.textContent.trim()),
                            markets: []
                        };
                        oddsBtns.forEach(btn => {
                            const market = btn.querySelector(".ta-infoTextName");
                            const price = btn.querySelector(".ta-price_text");
                            if (market && price) {
                                matchData.markets.push({
                                    name: market.textContent.trim(),
                                    value: price.textContent.trim()
                                });
                            }
                        });
                        if (matchData.teams.length > 0) results.push(matchData);
                    });
                    return results;
                }
                """)

                with open(os.path.join(OUTPUT_DIR, f"solverde_extracted_data_correct_url_{ts}.json"), "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"[SAVED] Extracted {len(data)} matches.")
            except Exception as e:
                print(f"Error extracting data: {e}")
        else:
            print("Could not find 'APOSTAS DESPORTIVAS' link.")
            # Save screenshot anyway for debugging
            ts = int(time.time())
            await page.screenshot(path=os.path.join(OUTPUT_DIR, f"solverde_menu_search_failed_{ts}.png"), full_page=True)
            print(f"[SAVED] Debug screenshot")

        await browser.close()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
