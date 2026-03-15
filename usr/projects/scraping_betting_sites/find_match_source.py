import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        responses = []
        ws_frames = []

        async def handle_response(response):
            if "sportswidget" in response.url and response.status == 200:
                try:
                    text = await response.text()
                    responses.append({"url": response.url, "body": text})
                except: pass

        def on_websocket(ws):
            ws.on("framereceived", lambda payload: ws_frames.append({"url": ws.url, "data": str(payload)}))

        page.on("response", handle_response)
        page.on("websocket", on_websocket)

        print("Navigating to: https://www.placard.pt/apostas/sports/soccer")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Bypassing cookie banner if needed
        try:
            await page.click("button:has-text('Aceitar')", timeout=5000)
        except: pass

        await asyncio.sleep(10)

        # Identify match names from the UI
        match_names = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('div'))
                .filter(d => d.innerText && d.innerText.includes(' - '))
                .map(d => d.innerText.split('\n')[0])
                .filter(t => t.length > 5);
        }''')
        print(f"Matches found in UI: {match_names[:5]}")

        # Search for match names in REST responses
        for res in responses:
            for name in match_names[:5]:
                if name in res["body"]:
                    print(f"MATCH NAME '{name}' FOUND IN REST: {res['url']}")

        # Search for match names in WS frames
        for frame in ws_frames:
            for name in match_names[:5]:
                if name in frame["data"]:
                    print(f"MATCH NAME '{name}' FOUND IN WS: {frame['url']}")
                    # Look for the subscription topic in nearby frames if possible

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
