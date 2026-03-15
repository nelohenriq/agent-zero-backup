import asyncio
import json
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        logs = {"api": [], "ws": []}

        # Capture WebSocket
        def on_websocket(ws):
            ws.on("framesent", lambda payload: logs["ws"].append({"dir": "SENT", "data": str(payload)}))
            ws.on("framereceived", lambda payload: logs["ws"].append({"dir": "RECV", "data": str(payload)}))
        page.on("websocket", on_websocket)

        # Capture API
        async def handle_response(response):
            url = response.url
            if "api" in url:
                try:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")
                        if "json" in content_type:
                            text = await response.text()
                            logs["api"].append({
                                "url": url,
                                "method": response.request.method,
                                "headers": response.request.headers,
                                "payload": response.request.post_data,
                                "response": text[:2000] # Limit size
                            })
                except: pass
        page.on("response", handle_response)

        print("Navigating to Soccer page...")
        await page.goto("https://www.placard.pt/apostas/soccer", wait_until="networkidle")
        await asyncio.sleep(10) # Wait for all dynamic loads

        # Try to find any match link or ID in the page
        print("Searching for matches...")
        ids = await page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a[href*="/apostas/evento/"]'));
            return links.map(l => l.href);
        }''')

        if ids:
            match_url = ids[0]
            print(f"Navigating to match detail: {match_url}")
            await page.goto(match_url, wait_until="networkidle")
            await asyncio.sleep(10)
        else:
            print("No match links found via selectors. Relying on network logs.")

        with open("/a0/usr/projects/scraping_betting_sites/investigation_raw.json", "w") as f:
            json.dump(logs, f, indent=2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
