import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        requests = []
        page.on("request", lambda request: requests.append(f"{request.method} {request.url}"))

        print("Navigating to pre-match soccer page...")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        await asyncio.sleep(10)

        print("\n--- All Requests Captured ---")
        for r in requests:
            if "sportswidget" in r:
                print(r)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
