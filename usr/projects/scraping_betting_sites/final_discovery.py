import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        discovered = []

        async def handle_response(response):
            url = response.url
            if "sportswidget" in url and response.status == 200:
                try:
                    text = await response.text()
                    if '"events":[' in text or '"marketLines":' in text:
                        print(f"FOUND: {url}")
                        discovered.append({"url": url, "headers": response.request.headers})
                except: pass

        page.on("response", handle_response)

        print("Navigating to Soccer Pre-Match...")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Wait for data to load
        await asyncio.sleep(10)

        with open("/a0/usr/projects/scraping_betting_sites/final_api_discovery.json", "w") as f:
            json.dump(discovered, f, indent=2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
