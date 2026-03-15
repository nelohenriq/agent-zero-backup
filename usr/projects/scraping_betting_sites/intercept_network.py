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

        intercepted_requests = []

        async def handle_request(request):
            if "sportswidget" in request.url or "api" in request.url:
                intercepted_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": request.headers
                })

        page.on("request", handle_request)

        print("Navigating to soccer page...")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Find the first match link and click it
        # Based on previous observations, match links often contain /events/
        try:
            match_link = await page.wait_for_selector("a[href*='/events/']", timeout=10000)
            if match_link:
                href = await match_link.get_attribute("href")
                print(f"Clicking on match: {href}")
                await match_link.click()
                await page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Could not find or click match link: {e}")

        print("Captured Requests:")
        relevant_requests = [r for r in intercepted_requests if "/api/" in r["url"]]
        for req in relevant_requests:
            print(f"URL: {req['url']}")
            print(f"Method: {req['method']}")
            # print(f"Headers: {req['headers']}") # Headers might be too long
            print("-" * 20)

        with open("/a0/usr/projects/scraping_betting_sites/captured_api_requests.json", "w") as f:
            json.dump(relevant_requests, f, indent=2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
