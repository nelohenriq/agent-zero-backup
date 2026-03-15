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
            url = response.url
            if "sportswidget" in url and response.status == 200:
                try:
                    content_type = response.headers.get("content-type", "")
                    if "json" in content_type:
                        text = await response.text()
                        # Check if this JSON contains match/event data
                        if '"events":[' in text or '"matches":[' in text:
                            print(f"[MATCH DATA] {url}")
                            found_endpoints.append({"url": url, "headers": response.request.headers})
                        elif '"marketGroups":[' in text:
                            print(f"[MARKET DATA] {url}")
                            found_endpoints.append({"url": url, "headers": response.request.headers})
                        else:
                            print(f"[JSON] {url}")
                except: pass

        page.on("response", handle_response)

        print("Navigating to Soccer Pre-Match page...")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Dismiss cookie banner to trigger widget loading
        try:
            await page.click("button:has-text('Aceitar')", timeout=5000)
            print("Cookies accepted.")
        except: pass

        await asyncio.sleep(10) # Wait for data to populate

        with open("/a0/usr/projects/scraping_betting_sites/discovered_endpoints.json", "w") as f:
            json.dump(found_endpoints, f, indent=2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
