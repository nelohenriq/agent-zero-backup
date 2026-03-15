"""Solverde WebSocket Frame Capture Script v4 - Fixed CDP usage"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports"
WS_LOG_FILE = os.path.join(OUTPUT_DIR, f"solverde_ws_frames_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
CAPTURE_FILE = os.path.join(OUTPUT_DIR, f"solverde_full_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

ws_frames = []
http_responses = []
ws_connections = []

def log_ws_frame(frame_type, data, timestamp):
    frame_entry = {
        "type": frame_type,
        "data": str(data)[:500],
        "timestamp": timestamp,
        "size": len(str(data))
    }
    ws_frames.append(frame_entry)
    print(f"[WS {frame_type}] {str(data)[:150]}...")

async def run():
    global ws_frames, http_responses, ws_connections
    
    print("=== Solverde WebSocket Frame Capture v4 ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Set up CDP session on page for WebSocket monitoring
        cdp = await page.new_cdp_session(page)
        
        # Enable WebSocket domain
        await cdp.send("WebSocket.enable")
        
        # WebSocket frame handlers
        async def on_ws_frame(params):
            timestamp = datetime.now().isoformat()
            if "request" in params:
                req = params["request"]
                url = req.get("url", "")
                ws_connections.append({"url": url, "timestamp": timestamp})
                log_ws_frame("CONNECT", url, timestamp)
            elif "frameReceived" in params:
                data = params.get("frameReceived", {}).get("text", "")
                log_ws_frame("RECV", data, timestamp)
            elif "frameSent" in params:
                data = params.get("frameSent", {}).get("text", "")
                log_ws_frame("SENT", data, timestamp)
        
        cdp.on("WebSocket.frameReceived", lambda params: asyncio.create_task(on_ws_frame(params)))
        cdp.on("WebSocket.frameSent", lambda params: asyncio.create_task(on_ws_frame(params)))
        cdp.on("WebSocket.requestWillBeSent", lambda params: asyncio.create_task(on_ws_frame(params)))
        
        # Navigate to Solverde
        print("Navigating to solverde.pt...")
        await page.goto("https://www.solverde.pt", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Try to click Futebol
        print("Looking for Futebol section...")
        selectors = [
            "[data-testid*='futebol']",
            "a[href*='futebol']",
            "button:has-text('Futebol')",
            "text=Futebol",
        ]
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    print(f"Found: {sel}")
                    await el.click()
                    await page.wait_for_timeout(5000)
                    break
            except:
                pass
        
        # Wait for live data
        print("\nWaiting for live data...")
        await page.wait_for_timeout(15000)
        
        # Scroll to trigger lazy loading
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3000)
        
        # Save results
        print(f"\n=== Capture Complete ===")
        print(f"WebSocket frames: {len(ws_frames)}")
        print(f"WS connections: {len(ws_connections)}")
        
        # Save WebSocket log
        ws_result = {
            "capture_time": datetime.now().isoformat(),
            "total_frames": len(ws_frames),
            "frames": ws_frames,
            "connections": ws_connections
        }
        
        with open(WS_LOG_FILE, "w") as f:
            json.dump(ws_result, f, indent=2)
        print(f"\nWebSocket log saved: {WS_LOG_FILE}")
        
        # Show sample
        if ws_frames:
            print("\n=== WebSocket Frame Samples ===")
            for frame in ws_frames[:10]:
                print(f"[{frame['type']}] {frame['data'][:100]}")
        else:
            print("\n⚠ No WebSocket frames captured!")
        
        await browser.close()
        return ws_result

if __name__ == "__main__":
    result = asyncio.run(run())
    print("\n✓ Capture complete!")
