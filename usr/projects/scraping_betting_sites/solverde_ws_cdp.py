"""
Solverde WebSocket Capture using Chrome DevTools Protocol (CDP)
Properly captures WebSocket frames via CDP session
"""
import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

ws_frames_sent = []
ws_frames_received = []
ws_connections = []

async def run():
    global ws_frames_sent, ws_frames_received, ws_connections
    
    p = await async_playwright().start()
    browser = await p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    context = await browser.new_context()
    page = await context.new_page()
    
    # Create CDP session for WebSocket monitoring
    cdp = await page.context.new_cdp_session(page)
    
    # Enable WebSocket tracking
    await cdp.send("Network.enable")
    
    # Listen for WebSocket frames via CDP
    def handlewebsocket(frame):
        ws_connections.append({
            "timestamp": datetime.now().isoformat(),
            "url": frame.get("request", {}).get("url", ""),
            "protocol": frame.get("protocol", "unknown")
        })
        print(f"[WS CONNECT] {frame.get('request', {}).get('url', '')[:80]}")
    
    cdp.on("WebSocket.created", lambda frame: ws_connections.append({
        "timestamp": datetime.now().isoformat(),
        "url": frame.get("request", {}).get("url", "")
    }))
    
    cdp.on("WebSocket.frameSent", lambda frame: ws_frames_sent.append({
        "timestamp": datetime.now().isoformat(),
        "data": frame.get("text", ""),
        "opcode": frame.get("opcode", 0)
    }))
    
    cdp.on("WebSocket.frameReceived", lambda frame: ws_frames_received.append({
        "timestamp": datetime.now().isoformat(),
        "data": frame.get("text", ""),
        "opcode": frame.get("opcode", 0)
    }))
    
    # Also capture HTTP
    http_responses = []
    async def handle_response(response):
        url = response.url
        if any(k in url.lower() for k in ["solverde", "futebol", "odds", "live", "match", "sport", "bet"]):
            try:
                body = await response.text()
            except:
                body = "[body unavailable]"
            http_responses.append({
                "url": url,
                "status": response.status,
                "body_length": len(body) if body else 0,
                "timestamp": datetime.now().isoformat()
            })
    
    page.on("response", handle_response)
    
    print("="*60)
    print("Solverde CDP WebSocket Capture")
    print("="*60)
    
    # Navigate
    print("\n[1] Opening Solverde.pt...")
    await page.goto("https://www.solverde.pt", timeout=30000)
    await page.wait_for_load_state("networkidle")
    
    print("[2] Clicking Futebol...")
    await page.click("text=Futebol", timeout=10000)
    await asyncio.sleep(2)
    
    print("[3] Capturing WebSocket traffic (30 seconds)...")
    for i in range(6):
        await asyncio.sleep(5)
        print(f"   {i*5}s - WS sent: {len(ws_frames_sent)}, received: {len(ws_frames_received)}, connections: {len(ws_connections)}")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "ws_connections": ws_connections,
        "ws_frames_sent": ws_frames_sent[:100],  # Limit
        "ws_frames_received": ws_frames_received[:100],
        "http_responses": http_responses[:100]
    }
    
    out_file = f"solverde_cdp_ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(f"/a0/usr/projects/scraping_betting_sites/{out_file}", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[Saved] {out_file}")
    print(f"WS Connections: {len(ws_connections)}")
    print(f"WS Frames Sent: {len(ws_frames_sent)}")
    print(f"WS Frames Received: {len(ws_frames_received)}")
    
    await browser.close()
    await p.stop()

if __name__ == "__main__":
    asyncio.run(run())
