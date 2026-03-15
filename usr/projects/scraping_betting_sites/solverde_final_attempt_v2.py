
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
        # Try direct sports URL first
        await page.goto("https://www.solverde.pt/pt-pt/apostas-desportivas", wait_until="domcontentloaded", timeout=60000)

        print("Waiting for initial load...")
        await asyncio.sleep(5)

        # 1. Handle Cookie Consent
        print("Looking for cookie acceptance button...")
        try:
            btn = await page.wait_for_selector(".EuAceitoBtn", timeout=5000)
            if btn:
                print("Clicking cookie button...")
                await btn.click(force=True)
                await asyncio.sleep(2)
        except Exception as e:
            print(f"Cookie button not found: {e}")

        # 2. Close Registration/Promotion Modal
        print("Looking for modal close button...")
        close_selectors = [
            "button[aria-label='Close']",
            "button[class*='close']",
            "button[class*='Close']",
            "button:has-text('X')",
            "button:has-text('Fechar')",
            ".modal-close",
            "button[data-dismiss='modal']",
            "button[class*='modal-close']",
            "button[class*='CloseButton']"
        ]

        modal_closed = False
        for selector in close_selectors:
            try:
                close_btn = await page.wait_for_selector(selector, timeout=3000)
                if close_btn and await close_btn.is_visible():
                    print(f"Found close button with selector: {selector}. Clicking...")
                    await close_btn.click(force=True)
                    await asyncio.sleep(2)
                    modal_closed = True
                    break
            except Exception as e:
                # print(f"Selector {selector} not found or timed out: {e}")
                pass

        if not modal_closed:
            print("Warning: Could not close modal. Proceeding anyway.")

        # 3. Ensure Sports Section is Active
        print("Checking if sports section is visible...")
        try:
            # Check if we are already on sports page
            await page.wait_for_selector(".ta-headerTitle", timeout=5000)
            print("Sports content already visible!")
        except Exception as e:
            print(f"Sports content not visible. Trying to navigate via menu...")
            # Try clicking "APOSTAS DESPORTIVAS" in menu
            try:
                menu_item = await page.wait_for_selector("text=APOSTAS DESPORTIVAS", timeout=5000)
                if menu_item:
                    print("Clicking 'APOSTAS DESPORTIVAS'...")
                    await menu_item.click(force=True)
                    await asyncio.sleep(5)
            except Exception as e:
                print(f"Could not click menu item: {e}")

        # 4. Wait for content
        print("Waiting for sports content to load...")
        try:
            await page.wait_for_selector(".ta-headerTitle", timeout=15000)
            print("Sports content detected!")
        except Exception as e:
            print(f"Sports content selector not found after all attempts: {e}")
            await asyncio.sleep(10)

        # 5. Save full HTML
        print("Saving full HTML...")
        html = await page.content()
        filename = f"solverde_final_v2_html_{int(time.time())}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[SAVED] {filename}")

        # 6. Take screenshot
        print("Taking screenshot...")
        screenshot_path = os.path.join(OUTPUT_DIR, f"solverde_final_v2_screenshot_{int(time.time())}.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"[SAVED] {screenshot_path}")

        # 7. Extract betting data
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

            data_file = os.path.join(OUTPUT_DIR, f"solverde_extracted_data_v2_{int(time.time())}.json")
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
