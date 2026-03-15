
import asyncio
import json
import os
import re
from playwright.async_api import async_playwright
import time

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports"
HTML_OUTPUT = os.path.join(OUTPUT_DIR, "solverde_full_source.html")
API_LOG = os.path.join(OUTPUT_DIR, "solverde_all_api_responses.json")

async def capture_all_data():
    print("Starting comprehensive capture script...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # Enable CDP for network interception
        await page.context.new_cdp_session(page)

        all_responses = []

        # Intercept all responses
        async def on_response(response):
            url = response.url
            try:
                # Try to get body via CDP if possible, or standard text
                # Note: response.text() might fail for large/compressed, but we try
                body = None
                try:
                    body = await response.text()
                except Exception as e:
                    # Fallback: try to get via CDP if available (complex, skipping for now, just log error)
                    pass

                if body and len(body) > 100: # Only save substantial responses
                    # Check if it looks like JSON
                    if "application/json" in response.headers.get("content-type", "") or (body.strip().startswith("{") or body.strip().startswith("[")):
                        all_responses.append({
                            "url": url,
                            "status": response.status,
                            "headers": dict(response.headers),
                            "body_preview": body[:1000],
                            "body_length": len(body)
                        })
                        print(f"[CAPTURED] {url} ({len(body)} bytes)")
            except Exception as e:
                print(f"Error processing {url}: {e}")

        page.on("response", on_response)

        print("Navigating to solverde.pt...")
        await page.goto("https://www.solverde.pt/", wait_until="networkidle")

        # Wait for initial load
        await page.wait_for_timeout(5000)

        # Click Desporto
        print("Clicking Desporto...")
        try:
            await page.click("text=Desporto", timeout=5000)
            await page.wait_for_timeout(10000) # Wait for data to load
        except:
            print("Could not click Desporto, waiting anyway.")
            await page.wait_for_timeout(10000)

        # Save HTML
        html_content = await page.content()
        with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved HTML to {HTML_OUTPUT}")

        # Save API responses
        with open(API_LOG, "w", encoding="utf-8") as f:
            json.dump(all_responses, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(all_responses)} API responses to {API_LOG}")

        # Also search HTML for JSON patterns
        json_pattern = re.compile(r"(\{[^{}]*(?:\{[^{}]*[^{}]*\})*[^{}]*\}|\[[^\[\]]*(?:\[[^\[\]]*[^\[\]]*\])*[^\[\]]*\])")
        found_jsons = json_pattern.findall(html_content)
        print(f"Found {len(found_jsons)} potential JSON blocks in HTML.")

        # Save first few large JSON blocks found in HTML
        html_json_log = os.path.join(OUTPUT_DIR, "solverde_html_json_blocks.json")
        with open(html_json_log, "w", encoding="utf-8") as f:
            # Filter for likely sports data (look for keys like 'odds', 'events', 'teams')
            valid_blocks = []
            for block in found_jsons:
                if len(block) > 500 and ("odds" in block.lower() or "events" in block.lower() or "teams" in block.lower()):
                    valid_blocks.append(block)
                    if len(valid_blocks) >= 5: # Limit to 5
                        break
            json.dump(valid_blocks, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(valid_blocks)} potential sports JSON blocks from HTML to {html_json_log}")

        await browser.close()
        print("Capture complete.")

if __name__ == "__main__":
    asyncio.run(capture_all_data())
