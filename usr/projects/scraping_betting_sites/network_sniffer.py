import asyncio
import json
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a real-looking user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        captured_json = []

        async def handle_response(response):
            if "sportswidget.placard.pt" in response.url:
                try:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")
                        if "json" in content_type:
                            body = await response.json()
                            captured_json.append({
                                "url": response.url,
                                "method": response.request.method,
                                "headers": response.request.headers,
                                "post_data": response.request.post_data,
                                "body": body
                            })
                except Exception as e:
                    pass

        page.on("response", handle_response)

        print("Navigating to Soccer page...")
        await page.goto("https://www.placard.pt/apostas/soccer", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(15) # Giving it plenty of time

        # Save screenshot for debugging
        await page.screenshot(path="/a0/usr/projects/scraping_betting_sites/soccer_page.png")
        
        # Find match links
        links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a'))
                .map(a => a.href)
                .filter(href => href.includes('/apostas/evento/'));
        }''')
        print(f"Found {len(links)} match links.")

        if links:
            print(f"Navigating to first match: {links[0]}")
            await page.goto(links[0], wait_until="networkidle")
            await asyncio.sleep(10)

        with open("/a0/usr/projects/scraping_betting_sites/network_dump.json", "w") as f:
            json.dump(captured_json, f, indent=2)

        print("Sniffing complete. Data saved to network_dump.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
