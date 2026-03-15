import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        ws_data = []

        def on_websocket(ws):
            print(f"[WS] Connected: {ws.url}")
            ws.on("framesent", lambda payload: print(f"[WS SENT] {payload[:200]}"))
            ws.on("framereceived", lambda payload: ws_data.append(payload))

        page.on("websocket", on_websocket)

        print("Navigating...")
        await page.goto("https://www.placard.pt/", wait_until="networkidle")

        # Wait for potential loading screens
        await asyncio.sleep(10)

        # Take a screenshot to debug visibility
        await page.screenshot(path="/a0/usr/projects/scraping_betting_sites/debug_screenshot.png", full_page=True)
        print("Screenshot saved.")

        # Analyze frames received
        for frame in ws_data[-20:]: # Check last 20 frames
            if isinstance(frame, str) and ('odds' in frame.lower() or 'event' in frame.lower()):
                print(f"[DATA FOUND IN WS] {frame[:500]}...")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())