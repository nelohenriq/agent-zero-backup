"""
Solverde WebSocket Frame Capture Script
Captures all WebSocket traffic including live odds streaming
"""

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
    """Log WebSocket frame to memory and file"""
    frame_entry = {
        "type": frame_type,
        "data": data,
        "timestamp": timestamp,
        "size": len(str(data))
    }
    ws_frames.append(frame_entry)
    print(f"[WS {frame_type}] {str(data)[:200]}...")

async def run():
    global ws_frames, http_responses, ws_connections
    
    print("=== Solverde WebSocket Frame Capture ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Set up WebSocket handler via CDP
        cdp = await context.new_cdp_session(browser)
        
        # Enable Network and WebSocket domains
        await cdp.send("Network.enable")
        await cdp.send("WebSocket.enable")
        
        # WebSocket frame handler
        def handle_ws_frame(params):
            timestamp = datetime.now().isoformat()
            if "request" in params:
                req = params["request"]
                ws_connections.append({
                    "url": req.get("url", ""),
                    "timestamp": timestamp
                })
                log_ws_frame("CONNECT", req.get("url", ""), timestamp)
            elif "response" in params:
                resp = params["response"]
                log_ws_frame("RESPONSE", resp.get("text", "")[:500], timestamp)
            elif "frame" in params:
                frame = params["frame"]
                log_ws_frame("FRAME", frame.get("text", "")[:500], timestamp)
            elif "error" in params:
                log_ws_frame("ERROR", params["error"], timestamp)
        
        # Register WebSocket event listener
        cdp.on("WebSocket.frameSent", lambda params: log_ws_frame("SENT", params.get("frame", {}).get("text", ""), datetime.now().isoformat()))
        cdp.on("WebSocket.frameReceived", lambda params: log_ws_frame("RECEIVED", params.get("frame", {}).get("text", ""), datetime.now().isoformat()))
        cdp.on("WebSocket.willSendHandshakeRequest", lambda params: log_ws_frame("WILL_SEND", params.get("request", {}).get("url", ""), datetime.now().isoformat()))
        cdp.on("WebSocket.handshakeResponseReceived", lambda params: log_ws_frame("HANDSHAKE", params.get("response", {}).get("url", ""), datetime.now().isoformat()))
        cdp.on("WebSocket.connectionAccepted", lambda params: log_ws_frame("ACCEPTED", params.get("request", {}).get("url", ""), datetime.now().isoformat()))
        
        # HTTP Response handler
        async def handle_response(response):
            url = response.url
            status = response.status
            
            # Capture relevant responses
            if any(kw in url for kw in ["solverde", "sports", "bet", "game", "live", "odds", "feed", "api"]):
                try:
                    body = await response.text()
                    http_responses.append({
                        "url": url,
                        "status": status,
                        "headers": dict(response.headers),
                        "body": body[:100000]  # Limit size
                    })
                    print(f"[HTTP {status}] {url[:80]}")
                except:
                    pass
        
        page = await context.new_page()
        page.on("response", handle_response)
        
        print("Opening Solverde.pt...")
        try:
            await page.goto("https://www.solverde.pt", timeout=30000)
            await page.wait_for_timeout(3000)
            print(f"Page loaded, title: {await page.title()}")
        except Exception as e:
            print(f"Initial load error: {e}")
        
        # Try clicking "Futebol" button
        print("\nLooking for Futebol section...")
        try:
            # Try multiple selectors for football/sports
            selectors = [
                "text=Futebol",
                "text=Desportos",
                "[data-testid*='futebol']",
                "a[href*='futebol']",
                "button:has-text('Futebol')",
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
        except Exception as e:
            print(f"Click error: {e}")
        
        # Wait for dynamic content
        print("\nWaiting for live data...")
        await page.wait_for_timeout(10000)
        
        # Scroll to trigger lazy loading
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3000)
        
        # Save results
        print(f"\n=== Capture Complete ===")
        print(f"WebSocket frames: {len(ws_frames)}")
        print(f"HTTP responses: {len(http_responses)}")
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
        
        # Save full capture
        with open(CAPTURE_FILE, "w") as f:
            json.dump(http_responses, f, indent=2)
        print(f"Full capture saved: {CAPTURE_FILE}")
        
        # Show sample of WS data
        if ws_frames:
            print("\n=== WebSocket Frame Samples ===")
            for frame in ws_frames[:5]:
                print(f"[{frame['type']}] {frame['data'][:100]}")
        else:
            print("\n⚠ No WebSocket frames captured!")
            print("Trying direct WebSocket connection...")
            
        await browser.close()
    
    return ws_result

if __name__ == "__main__":
    result = asyncio.run(run())
    print("\n✓ Capture complete!")

