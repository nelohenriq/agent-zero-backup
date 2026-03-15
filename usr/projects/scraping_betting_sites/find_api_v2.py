import asyncio
import json
import re
from playwright.async_api import async_playwright

async def handle_response(response):
    url = response.url
    resource_type = response.request.resource_type

    # Target the sports widget domain specifically
    if "sportswidget.placard.pt" in url or "placard.pt" in url:
        # Skip static assets and translations we already saw
        if any(ext in url for ext in ['.js', '.css', '.png', '.svg', '.woff', 'translations', 'initialResources']):
            return

        try:
            body = await response.json()
            # Filter for data-heavy responses
            body_str = json.dumps(body)
            keywords = ['odds', 'match', 'event', 'fixture', 'market', 'competition', 'participants']

            if any(k in body_str.lower() for k in keywords) or any(k in url.lower() for k in keywords):
                print(f"\n[DATA API] URL: {url}")
                print(f"Resource Type: {resource_type}")

                if isinstance(body, list):
                    print(f"Items count: {len(body)}")
                    print(f"Sample: {json.dumps(body[:1], indent=2)}")
                elif isinstance(body, dict):
                    # Print structure rather than full data if it's large
                    keys = list(body.keys())
                    print(f"Keys: {keys}")
                    # If there's a 'data' or 'events' key, sample that
                    for k in ['data', 'events', 'fixtures', 'markets']:
                        if k in body and body[k]:
                            val = body[k]
                            sample = val[:1] if isinstance(val, list) else val
                            print(f"Sample for '{k}': {json.dumps(sample, indent=2)[:500]}...")
                            break
                else:
                    print(f"Raw response sample: {str(body)[:200]}")
        except Exception:
            pass

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Listen for WebSocket
        page.on("websocket", lambda ws: print(f"[WS OPENED] {ws.url}"))

        page.on("response", handle_response)

        print("Navigating and waiting for content...")
        await page.goto("https://www.placard.pt/", wait_until="networkidle")

        # Try to click 'Futebol' or similar if visible to trigger requests
        try:
            # Look for common sport links
            await page.wait_for_selector("text=Futebol", timeout=5000)
            await page.click("text=Futebol")
            print("Clicked 'Futebol' category.")
            await asyncio.sleep(3)
        except:
            print("Could not find 'Futebol' link, continuing with scroll...")

        print("Scrolling...")
        for _ in range(10):
            await page.mouse.wheel(0, 800)
            await asyncio.sleep(1.5)

        print("Exploration finished.")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())