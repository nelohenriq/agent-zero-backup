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

        found_data = {"eventgroups": None, "markets": None, "match_id": None}

        async def handle_response(response):
            url = response.url
            if "sportswidget.placard.pt/api/" in url:
                try:
                    if response.status == 200:
                        text = await response.text()
                        if "eventgroups" in url and not found_data["eventgroups"]:
                            found_data["eventgroups"] = {"url": url, "sample": text[:1000]}
                            # Try to extract a match ID
                            data = json.loads(text)
                            if isinstance(data, dict) and "events" in data:
                                found_data["match_id"] = data["events"][0]["id"]
                        elif ("markets" in url or "events/" in url) and not found_data["markets"]:
                            found_data["markets"] = {"url": url, "method": response.request.method, "sample": text[:1000]}
                except: pass

        page.on("response", handle_response)

        print("Navigating to Soccer Pre-Match...")
        await page.goto("https://www.placard.pt/apostas/soccer", wait_until="networkidle")
        await asyncio.sleep(10)

        if found_data["match_id"]:
            mid = found_data["match_id"]
            print(f"Found Match ID: {mid}. Navigating to detail page...")
            await page.goto(f"https://www.placard.pt/apostas/evento/{mid}", wait_until="networkidle")
            await asyncio.sleep(10)
        else:
            # Fallback: try to find any link to a match
            print("No ID in eventgroups yet, looking for links...")
            links = await page.evaluate('''() => Array.from(document.querySelectorAll('a[href*="/apostas/evento/"]')).map(a => a.href)''')
            if links:
                print(f"Navigating to link: {links[0]}")
                await page.goto(links[0], wait_until="networkidle")
                await asyncio.sleep(10)

        print("\n--- INVESTIGATION RESULTS ---")
        print(json.dumps(found_data, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
