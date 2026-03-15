#!/usr/bin/env python3
"""
Solverde WebSocket Frame Capture - Enhanced Version
Intercepts all WebSocket frames (ws:// and wss://) and captures betting data
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_FILE = f"/a0/usr/projects/scraping_betting_sites/processed_sports/ws_frame_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

ws_traffic = {
    "connections": [],
    "frames_sent": [],
    "frames_received": [],
    "errors": []
}

async def intercept_cdp_ws(ws_url, ws_proto):
    """Handle WebSocket interception via CDP"""
    conn_info = {
        "url": ws_url,
        "protocol": ws_proto,
        "timestamp": datetime.now().isoformat()
    }
    ws_traffic["connections"].append(conn_info)
    print(f"[WS CONNECT] {ws_url} ({ws_proto})")
    return ws_url

async def main():
    print("=== Solverde WebSocket Frame Capture ===")
    print(f"Output: {OUTPUT_FILE}\n")
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,
        args=['--disable-web-security', '--allow-running-insecure-content']
    )
    
    context = await browser.new_context()
    page = await context.new_page()
    
    # Track all WebSocket frames
    ws_frames = []
    
    # Method 1: Using page.on("weblogs") - captures WebSocket logs
    page.on("weblog", lambda ws: ws_frames.append({
        "type": "log",
        "url": ws.get("url", ""),
        "direction": ws.get("direction", ""),
        "message": ws.get("message", "")[:500] if ws.get("message") else "",
        "timestamp": datetime.now().isoformat()
    }))
    
    # Method 2: Listen for request/response with WS protocol
    page.on("request", lambda req: 
        ws_traffic["frames_sent"].append({
            "url": req.url,
            "method": req.method,
            "timestamp": datetime.now().isoformat()
        }) if req.url.startswith("ws") else None
    )
    
    page.on("response", lambda res: 
        ws_traffic["frames_received"].append({
            "url": res.url,
            "status": res.status,
            "timestamp": datetime.now().isoformat()
        }) if res.url.startswith("ws") else None
    )
    
    print("[*] Navigating to Solverde.pt...")
    try:
        await page.goto("https://www.solverde.pt", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception as e:
        print(f"[ERROR] Navigation: {e}")
        ws_traffic["errors"].append(str(e))
    
    print("[*] Waiting for page to initialize...")
    await asyncio.sleep(3)
    
    # Click on Futebol section
    print("[*] Looking for Futebol button...")
    try:
        # Try multiple selectors
        for selector in [
            "text=Futebol",
            "a[href*='futebol']",
            "button:has-text('Futebol')",
            "div:has-text('Futebol')",
            "[class*='sport'][class*='football']"
        ]:
            try:
                await page.click(selector, timeout=3000)
                print(f"[+] Clicked: {selector}")
                break
            except:
                continue
        await asyncio.sleep(5)
    except Exception as e:
        print(f"[WARN] Click failed: {e}")
    
    # Scan for any WebSocket connections in page
    print("\n[*] Scanning for WebSocket connections...")
    
    # Get all WebSocket URLs from the page
    ws_list = await page.evaluate("""
        () => {
            const ws = [];
            // Check if any WS objects exist
            if (window.WebSocket) {
                ws.push("WebSocket API available");
            }
            // Check network connections
            return ws;
        }
    """)
    print(f"[i] Browser WS info: {ws_list}")
    
    # Let site load live data
    print("\n[*] Waiting for live data (10s)...")
    await asyncio.sleep(10)
    
    # Get current WebSocket frames
    print(f"\n[+] WebSocket frame count: {len(ws_frames)}")
    for frame in ws_frames[:10]:
        print(f"  - {frame.get('direction', '?')}: {frame.get('message', '')[:100]}")
    
    # Save results
    result = {
        "timestamp": datetime.now().isoformat(),
        "url": "https://www.solverde.pt",
        "ws_connections": ws_traffic["connections"],
        "ws_frames": ws_frames[:100],  # Limit to 100
        "http_ws_requests": {
            "sent": ws_traffic["frames_sent"],
            "received": ws_traffic["frames_received"]
        },
        "errors": ws_traffic["errors"]
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n[✓] Saved to: {OUTPUT_FILE}")
    print(f"  - Connections: {len(ws_traffic['connections'])}")
    print(f"  - Frames: {len(ws_frames)}")
    print(f"  - WS HTTP requests: {len(ws_traffic['frames_sent'])}")
    
    await browser.close()
    await playwright.stop()

if __name__ == "__main__":
    asyncio.run(main())
