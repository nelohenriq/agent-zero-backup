import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        found_api = []

        async def handle_response(response):
            url = response.url
            if "sportswidget" in url and response.status == 200:
                try:
                    if "json" in response.headers.get("content-type", ""):
                        text = await response.text()
                        if '"events":[' in text:
                            print(f"Found Match List API: {url}")
                            found_api.append({"type": "match_list", "url": url, "headers": response.request.headers})
                        elif '"marketLines":{' in text:
                            print(f"Found Event Detail API: {url}")
                            found_api.append({"type": "event_detail", "url": url, "headers": response.request.headers})
                except: pass

        page.on("response", handle_response)

        print("Navigating to https://www.placard.pt/apostas/sports/soccer")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Click cookie banner
        try:
            await page.click("button:has-text('Aceitar')", timeout=5000)
        except: pass

        await asyncio.sleep(10)

        with open("/a0/usr/projects/scraping_betting_sites/detected_api.json", "w") as f:
            json.dump(found_api, f, indent=2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
