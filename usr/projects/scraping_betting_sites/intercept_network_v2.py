import asyncio
import json
import sys
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        captured = []

        async def handle_request(request):
            if "sportswidget" in request.url:
                captured.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": request.headers,
                    "post_data": request.post_data
                })

        page.on("request", handle_request)

        # Use a known ID from prefetch.json if possible, or navigate to soccer first
        target_url = "https://www.placard.pt/apostas/sports/soccer"
        print(f"Navigating to {target_url}...")
        await page.goto(target_url, wait_until="networkidle")
        
        # Wait for a bit to capture initial prefetch/discovery calls
        await asyncio.sleep(5)

        # Find and click a match
        try:
            match_link = await page.wait_for_selector("a[href*='/events/']", timeout=10000)
            href = await match_link.get_attribute("href")
            full_href = f"https://www.placard.pt{href}" if href.startswith("/") else href
            print(f"Navigating directly to match: {full_href}")
            await page.goto(full_href, wait_until="networkidle")
            await asyncio.sleep(5) # Wait for markets to load
        except Exception as e:
            print(f"Error clicking/navigating to match: {e}")

        print(f"Captured {len(captured)} requests to sportswidget.")
        
        # Filter for interesting ones
        interesting = [c for c in captured if "/api/events/" in c["url"] or "/api/markets/" in c["url"] or "pre-fetch" in c["url"]]
        
        with open("/a0/usr/projects/scraping_betting_sites/captured_api_v2.json", "w") as f:
            json.dump(interesting, f, indent=2)

        for i in interesting:
            print(f"FOUND: {i['url']} [{i['method']}]")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
