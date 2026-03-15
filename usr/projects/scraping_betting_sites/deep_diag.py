import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        found_endpoints = []

        async def handle_response(response):
            if "sportswidget.placard.pt" in response.url:
                try:
                    if response.status == 200:
                        found_endpoints.append({
                            "url": response.url,
                            "method": response.request.method,
                            "headers": response.request.headers
                        })
                except: pass

        page.on("response", handle_response)

        print("Navigating to: https://www.placard.pt/apostas/sports/soccer")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Try to click cookie button
        try:
            await page.click("button:has-text('Aceitar')", timeout=5000)
            print("Cookie banner accepted.")
        except: 
            print("Cookie banner not found or already dismissed.")

        await asyncio.sleep(10) # Wait for event list loading
        
        print("\n--- Found Sportswidget Endpoints ---")
        for ep in found_endpoints:
            if "eventgroups" in ep["url"] or "events" in ep["url"]:
                print(f"{ep['method']} {ep['url']}")
                print(f"Headers: {json.dumps(ep['headers'], indent=2)}")
                print("-" * 40)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
