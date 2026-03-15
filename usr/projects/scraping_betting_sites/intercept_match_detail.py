import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        captured_requests = []

        async def handle_request(request):
            if "api" in request.url and "sportswidget" in request.url:
                captured_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": request.headers
                })

        page.on("request", handle_request)

        # Use one of the fresh IDs found earlier: 12561047983
        target_url = "https://www.placard.pt/apostas/sports/soccer/events/12561047983"
        print(f"Navigating to {target_url}...")
        try:
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(5) # Wait for final markets to load
        except Exception as e:
            print(f"Navigation failed: {e}")

        print(f"Captured {len(captured_requests)} relevant API requests.")
        with open("/a0/usr/projects/scraping_betting_sites/match_detail_capture.json", "w") as f:
            json.dump(captured_requests, f, indent=2)
        
        for req in captured_requests:
            if "events" in req["url"] or "markets" in req["url"]:
                print(f"FOUND: {req['url']} ({req['method']})")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
