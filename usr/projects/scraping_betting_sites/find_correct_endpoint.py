import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        found_url = None

        async def handle_response(response):
            nonlocal found_url
            url = response.url
            if "sportswidget.placard.pt" in url and response.status == 200:
                try:
                    text = await response.text()
                    if '"events":[' in text or '"id":"soccer' in text:
                        print(f"MATCH FOUND: {url}")
                        found_url = url
                except: pass

        page.on("response", handle_response)

        print("Navigating to: https://www.placard.pt/apostas/sports/soccer")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="domcontentloaded")
        
        # Click cookie banner if it appears
        try:
            await page.click("button:has-text('Aceitar')", timeout=5000)
            print("Cookies accepted.")
        except: pass

        await asyncio.sleep(15) # Long wait for widget data

        if not found_url:
            print("No matching API call found. Dumping all sportswidget calls:")
            # Fallback debug
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
