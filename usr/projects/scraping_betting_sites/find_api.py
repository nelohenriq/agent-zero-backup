import asyncio
import json
from playwright.async_api import async_playwright

async def handle_response(response):
    content_type = response.headers.get('content-type', '')
    url = response.url

    # Check for JSON responses or common API patterns
    if 'application/json' in content_type or response.request.resource_type in ['fetch', 'xhr']:
        try:
            # Ignore tracking/analytics
            if any(domain in url for domain in ['google-analytics', 'facebook', 'hotjar', 'doubleclick', 'sentry']):
                return

            body = await response.json()
            print(f"\n[API FOUND] URL: {url}")
            print(f"Content-Type: {content_type}")

            # Sample the JSON (first few keys or items)
            if isinstance(body, list):
                print(f"Sample (list): {json.dumps(body[:1], indent=2)}")
            elif isinstance(body, dict):
                sample = {k: body[k] for k in list(body.keys())[:5]}
                print(f"Sample (dict): {json.dumps(sample, indent=2)}")
            else:
                print(f"Body: {str(body)[:200]}...")

        except Exception:
            # Not JSON or failed to parse
            pass

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a real user agent to avoid bot detection
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        page.on("response", handle_response)

        print("Navigating to https://www.placard.pt/...")
        await page.goto("https://www.placard.pt/", wait_until="networkidle")

        print("Scrolling to trigger lazy loading...")
        for _ in range(5):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)

        print("Finished exploration.")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())