import asyncio
import json
from playwright.async_api import async_playwright

async def capture_soccer_events():
    result = {
        "timestamp": None,
        "url": "https://www.solverde.pt/apostas/desportivas",
        "ws_endpoint": "wss://sports-ws.solverde.pt/ws",
        "subscription_sent": None,
        "events_received": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set up WebSocket handler BEFORE navigation
        ws_frames = []
        
        def handle_request(request):
            if "ws" in request.url.lower() or "websocket" in request.url.lower():
                print(f"WS Request: {request.url}")
        
        page.on("request", handle_request)
        
        # Navigate to page
        print("Loading page...")
        await page.goto("https://www.solverde.pt/apostas/desportivas", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Click on Futebol section if available
        try:
            await page.locator("text=Futebol").first.click(timeout=5000)
            print("Clicked Futebol")
            await page.wait_for_timeout(3000)
        except:
            print("Futebol button not found, continuing...")
        
        # Try direct WebSocket connection
        ws_endpoints = [
            "wss://sports-ws.solverde.pt/ws",
            "wss://ws.solverde.pt/sports",
            "wss://live.solverde.pt/ws"
        ]
        
        for endpoint in ws_endpoints:
            print(f"Testing: {endpoint}")
            try:
                ws = await page.context.new_cdp_session(page).new_web_socket_session()
                # Just log that we found it
                print(f"Found WS endpoint: {endpoint}")
            except Exception as e:
                print(f"Failed: {e}")
        
        # Get all network requests for API calls
        print("\nGathering API calls...")
        
        await browser.close()
    
    # Save result
    with open("processed_sports/ws_fresh_capture.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nSaved to ws_fresh_capture.json")

asyncio.run(capture_soccer_events())
