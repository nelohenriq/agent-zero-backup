#!/usr/bin/env python3
"""Solverde WebSocket Frame Capture - Enhanced"""
import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_FILE = f"/a0/usr/projects/scraping_betting_sites/processed_sports/ws_frame_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

ws_data = {"connections": [], "sent": [], "received": [], "errors": []}

async def main():
    print("=== Solverde WebSocket Frame Capture ===")
    
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    
    # WebSocket frame tracking
    ws_frames = []
    
    # Capture WebSocket frames via CDP
    async def handle_weblog(ws):
        ws_frames.append({
            "url": ws.get("url", ""),
            "direction": ws.get("direction", "?"),
            "message": ws.get("message", "")[:500],
            "time": datetime.now().isoformat()
        })
    
    page.on("weblog", handle_weblog)
    
    # Navigate to Solverde
    print("[*] Opening solverde.pt...")
    await page.goto("https://www.solverde.pt", wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(3)
    
    # Find and click "Futebol" button
    print("[*] Clicking Futebol...")
    selectors = [
        "text=Futebol", "a:has-text('Futebol')", "[data-sport='futebol']",
        "button:has-text('Futebol')", "nav a:has-text('Futebol')"
    ]
    for sel in selectors:
        try:
            await page.click(sel, timeout=3000)
            print(f"[+] Clicked: {sel}")
            break
        except:
            continue
    
    await asyncio.sleep(8)
    
    # Collect WebSocket info
    result = {
        "timestamp": datetime.now().isoformat(),
        "url": "https://www.solverde.pt",
        "frames": ws_frames[:50],
        "frame_count": len(ws_frames)
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Saved: {OUTPUT_FILE}")
    print(f"    Frames captured: {len(ws_frames)}")
    
    await browser.close()
    await pw.stop()

if __name__ == "__main__":
    asyncio.run(main())
