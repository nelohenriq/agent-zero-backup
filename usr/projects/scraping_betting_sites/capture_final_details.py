import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        requests_log = []

        async def handle_request(request):
            if "api/events" in request.url or "api/markets" in request.url or "pre-fetch" in request.url:
                requests_log.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": request.headers,
                    "post_data": request.post_data
                })

        page.on("request", handle_request)

        print("Navigating to soccer page to find a match...")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Find the first match link and navigate to it
        try:
            match_link = await page.wait_for_selector("a[href*='/events/']", timeout=10000)
            match_url = await match_link.get_attribute("href")
            if match_url.startswith("/"):
                match_url = f"https://www.placard.pt{match_url}"
            
            print(f"Navigating to match detail: {match_url}")
            await page.goto(match_url, wait_until="networkidle")
            await asyncio.sleep(5) # Wait for all markets to load
        except Exception as e:
            print(f"Failed to navigate to match: {e}")

        print(f"Captured {len(requests_log)} relevant requests.")
        with open("/a0/usr/projects/scraping_betting_sites/final_capture.json", "w") as f:
            json.dump(requests_log, f, indent=2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
