"""
Solverde.pt WebSocket Scraper - Captures live betting data from framegas.com
"""
import json
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import sys

WS_MESSAGES = []

def save_and_exit():
    output = {
        "capture_time": datetime.now().isoformat(),
        "source": "solverde.pt - openapi.framegas.com WebSocket",
        "total_messages": len(WS_MESSAGES),
        "messages": WS_MESSAGES
    }
    with open("/a0/usr/projects/scraping_betting_sites/solverde_websocket_data.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n💾 Saved {len(WS_MESSAGES)} WebSocket messages to solverde_websocket_data.json")

async def scrape_websocket():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
        )
        
        page = await context.new_page()
        
        # WebSocket event handlers
        async def handle_ws(ws):
            print(f"🔗 WebSocket connected: {ws.url}")
            
            async def on_message(msg):
                try:
                    data = json.loads(msg)
                    entry = {
                        "timestamp": datetime.now().isoformat(),
                        "direction": "incoming",
                        "data": data,
                        "raw": msg[:500] if len(msg) > 500 else msg
                    }
                    WS_MESSAGES.append(entry)
                    # Print summary of message type
                    if isinstance(data, dict) and 'event' in str(data):
                        print(f"📨 [{len(WS_MESSAGES)}] Event: {data.get('event', 'unknown')}")
                except:
                    entry = {
                        "timestamp": datetime.now().isoformat(),
                        "direction": "incoming",
                        "raw": msg[:300]
                    }
                    WS_MESSAGES.append(entry)
                
                if len(WS_MESSAGES) >= 200:
                    print("✅ Collected 200 messages, closing...")
                    await browser.close()
                    save_and_exit()
                    sys.exit(0)
            
            ws.on("framereceived", on_message)
            ws.on("framereceived", lambda msg: asyncio.create_task(on_message(msg)))
        
        page.on("websocket", lambda ws: asyncio.create_task(handle_ws(ws)))
        
        # Network interception for Socket.IO polling
        async def handle_route(route, request):
            await route.continue_()
        
        await page.route("**/*", handle_route)
        
        print("🚀 Navigating to solverde.pt...")
        try:
            await page.goto("https://www.solverde.pt", timeout=60000, wait_until="networkidle")
        except:
            pass
        
        # Wait for sports/section to load and click
        print("⏳ Waiting for page to initialize WebSocket connections...")
        await asyncio.sleep(5)
        
        # Try to navigate to sports section
        try:
            await page.click("text=Desporto", timeout=10000)
            print("🏆 Clicked 'Desporto' (Sports)")
            await asyncio.sleep(3)
        except:
            try:
                await page.click("text=Apostas", timeout=5000)
                print("🏆 Clicked 'Apostas'")
            except:
                pass
        
        # Scroll to trigger more data loading
        print("⏳ Waiting for WebSocket data streaming...")
        for i in range(12):
            await asyncio.sleep(5)
            print(f"⏱️ T+{(i+1)*5}s - Messages: {len(WS_MESSAGES)}")
            
            # Scroll to load more
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            
            # Click on a match if available
            if i == 3:
                try:
                    matches = await page.query_selector_all('[class*="odd"], [class*="match"], .event-row')
                    if matches:
                        await matches[0].click()
                        print("🖱️ Clicked on first match")
                        await asyncio.sleep(2)
                except:
                    pass
        
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(scrape_websocket())
    except KeyboardInterrupt:
        pass
    finally:
        save_and_exit()
