
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
        await page.goto("https://www.solverde.pt/pt-pt/apostas-desportivas", wait_until="domcontentloaded", timeout=60000)

        print("Waiting for initial load...")
        await asyncio.sleep(5)

        # 1. Handle Cookie Consent - Try multiple selectors
        print("Looking for cookie acceptance button...")
        accept_buttons = [
            ".EuAceitoBtn",
            ".CookiesRegulationMessage__accept",
            "button:has-text('Eu aceito')",
            "button:has-text('EU ACEITO')"
        ]

        clicked = False
        for selector in accept_buttons:
            try:
                btn = await page.wait_for_selector(selector, timeout=3000)
                if btn:
                    print(f"Found button with selector: {selector}. Clicking...")
                    await btn.click(force=True)
                    await asyncio.sleep(3)
                    clicked = True
                    break
            except Exception as e:
                print(f"Selector {selector} not found or timed out: {e}")

        if not clicked:
            print("Warning: Could not click cookie button. Proceeding anyway.")

        # 2. Wait for sports content
        print("Waiting for sports content to load...")
        try:
            await page.wait_for_selector(".ta-headerTitle", timeout=15000)
            print("Sports content detected!")
        except Exception as e:
            print(f"Sports content selector not found: {e}. Waiting extra time...")
            await asyncio.sleep(10)

        # 3. Save full HTML
        print("Saving full HTML...")
        html = await page.content()
        filename = f"solverde_final_html_{int(time.time())}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[SAVED] {filename}")

        # 4. Take screenshot
        print("Taking screenshot...")
        screenshot_path = os.path.join(OUTPUT_DIR, f"solverde_final_screenshot_{int(time.time())}.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"[SAVED] {screenshot_path}")

        # 5. Extract betting data directly using Playwright
        print("Extracting betting data...")
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

                        if (matchData.teams.length > 0) {
                            results.push(matchData);
                        }
                    });
                    return results;
                }
            """)

            data_file = os.path.join(OUTPUT_DIR, f"solverde_extracted_data_{int(time.time())}.json")
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[SAVED] {data_file}")
            print(f"Found {len(data)} matches.")

        except Exception as e:
            print(f"Error extracting data: {e}")

        await browser.close()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
