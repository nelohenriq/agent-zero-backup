"""Solverde WebSocket Frame Capture Script v5 - Fixed CDP session"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports"
WS_LOG_FILE = os.path.join(OUTPUT_DIR, f"solverde_ws_frames_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

ws_frames = []
ws_connections = []

async def run():
 global ws_frames, ws_connections
 
 print("=== Solverde WebSocket Frame Capture v5 ===\n")
 
 async with async_playwright() as p:
 browser = await p.chromium.launch(headless=True)
 context = await browser.new_context()
 page = await context.new_page()
 
 # Create CDP session on the PAGE (not browser)
 cdp = await context.new_cdp_session(page)
 
 # Enable WebSocket domain
 await cdp.send("WebSocket.enable")
 
 print("CDP session created, monitoring WebSockets...")
 
 # WebSocket event handlers
 cdp.on("WebSocket.frameReceived", lambda params: print(f"[WS RECV] {str(params)[:100]}"))
 cdp.on("WebSocket.frameSent", lambda params: print(f"[WS SENT] {str(params)[:100]}"))
 cdp.on("WebSocket.requestWillBeSent", lambda params: print(f"[WS REQUEST] {str(params)[:100]}"))
 
 # Also use page.on for standard WS frames
 page.on("websocket", lambda ws: print(f"[WS CONNECT] {ws.url}") or ws_connections.append(ws.url))
 
 # Navigate to Solverde
 print("\nNavigating to solverde.pt...")
 await page.goto("https://www.solverde.pt", wait_until="domcontentloaded", timeout=30000)
 await page.wait_for_timeout(3000)
 
 # Click Futebol
 print("Looking for Futebol...")
 try:
 await page.click("text=Futebol", timeout=5000)
 print("Clicked Futebol")
 except Exception as e:
 print(f"Could not click Futebol: {e}")
 
 # Wait for data
 print("\nWaiting for live data...")
 await page.wait_for_timeout(15000)
 
 # Save results
 result = {
 "capture_time": datetime.now().isoformat(),
 "total_ws": len(ws_connections),
 "connections": ws_connections
 }
 
 with open(WS_LOG_FILE, "w") as f:
 json.dump(result, f, indent=2)
 
 print(f"\n=== Results ===")
 print(f"WebSocket connections: {len(ws_connections)}")
 for url in ws_connections:
 print(f"  - {url}")
 
 await browser.close()
 return result

if __name__ == "__main__":
 result = asyncio.run(run())
 print("\n✓ Done!")
