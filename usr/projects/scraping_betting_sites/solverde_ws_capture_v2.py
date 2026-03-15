"""
Solverde WebSocket Capture v2
Focuses on capturing WebSocket traffic for live odds
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Storage for captured data
ws_connections = []
ws_messages_sent = []
ws_messages_received = []
network_requests = []

def save_results():
    """Save all captured data to JSON files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save WebSocket data
    ws_data = {
        "capture_time": timestamp,
        "connections": ws_connections,
        "messages_sent": ws_messages_sent,
        "messages_received": ws_messages_received,
        "connection_count": len(ws_connections)
    }
    
    ws_file = os.path.join(OUTPUT_DIR, f"solverde_ws_capture_{timestamp}.json")
    with open(ws_file, "w", encoding="utf-8") as f:
        json.dump(ws_data, f, indent=2, ensure_ascii=False)
    print(f"\n[WS] Saved WebSocket data to: {ws_file}")
    
    # Save network requests
    if network_requests:
        req_file = os.path.join(OUTPUT_DIR, f"solverde_network_{timestamp}.json")
        with open(req_file, "w", encoding="utf-8") as f:
            json.dump(network_requests, f, indent=2, ensure_ascii=False)
        print(f"[WS] Saved network requests to: {req_file}")
    
    return ws_file, ws_data

async def run():
    """Main capture function with WebSocket interception"""
    print("=" * 60)
    print("Solverde WebSocket Capture v2")
    print("=" * 60)
    
    global ws_connections, ws_messages_sent, ws_messages_received, network_requests
    
    async with async_playwright() as p:
        # Launch browser with full logging
        context = await p.chromium.launch_persistent_context(
            user_data_dir="/tmp/solverde_user_data",
            headless=True,  # Keep visible to ensure WebSocket connections
            
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--ignore-certificate-errors'
            ]
        )
        
        # Get the first page
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Set up WebSocket handler BEFORE navigation
        page.on("websocket", lambda ws: handle_websocket(ws))
        
        # Also capture network requests
        page.on("request", lambda request: capture_request(request))
        page.on("response", lambda response: capture_response(response))
        
        print("\n[1] Navigating to Solverde.pt...")
        try:
            await page.goto("https://www.solverde.pt", timeout=30000)
            print(f"[OK] Page loaded: {page.url}")
        except Exception as e:
            print(f"[ERROR] Failed to load page: {e}")
            await context.close()
            return
        
        # Wait for initial page to settle
        await asyncio.sleep(3)
        
        print("\n[2] Looking for 'Futebol' button...")
        try:
            # Try multiple selectors for the Futebol button
            futbol_selectors = [
                "text=Futebol",
                "a:has-text('Futebol')",
                "button:has-text('Futebol')",
                "[class*='futebol']",
                "xpath=//a[contains(@href, 'futebol')]",
            ]
            
            futbol_btn = None
            for selector in futbol_selectors:
                try:
                    futbol_btn = await page.wait_for_selector(selector, timeout=3000)
                    if futbol_btn:
                        print(f"[OK] Found Futebol button with selector: {selector}")
                        break
                except:
                    continue
            
            if futbol_btn:
                await futbol_btn.click()
                print("[OK] Clicked Futebol button")
                await asyncio.sleep(5)  # Wait for data to load via WebSocket
            else:
                print("[WARN] Futebol button not found, continuing anyway...")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"[WARN] Error clicking Futebol: {e}")
            await asyncio.sleep(5)
        
        # Check current WebSocket status
        print(f"\n[3] WebSocket Status:")
        print(f"    - Connections captured: {len(ws_connections)}")
        print(f"    - Messages sent: {len(ws_messages_sent)}")
        print(f"    - Messages received: {len(ws_messages_received)}")
        
        # List any WebSocket URLs found
        if ws_connections:
            print("\n    WebSocket URLs found:")
            for ws in ws_connections:
                print(f"      - {ws.get('url', 'unknown')}")
        
        # Wait longer for live odds via WebSocket
        print("\n[4] Waiting for live odds data (15 seconds)...")
        await asyncio.sleep(15)
        
        # Print final status
        print(f"\n[5] Final WebSocket Status:")
        print(f"    - Total connections: {len(ws_connections)}")
        print(f"    - Total messages sent: {len(ws_messages_sent)}")
        print(f"    - Total messages received: {len(ws_messages_received)}")
        
        # Try to access known WebSocket endpoint directly
        print("\n[6] Testing direct WebSocket connection to /ws/sports...")
        try:
            ws_url = "wss://www.solverde.pt/ws/sports"
            ws_test = await page.evaluate(f"""
                new Promise((resolve, reject) => {{
                    const ws = new WebSocket("{ws_url}");
                    ws.onopen = () => {{
                        ws.send(JSON.stringify({{type: 'ping'}}));
                        resolve({{status: 'connected', url: ws.url}});
                    }};
                    ws.onmessage = (e) => {{
                        console.log('WS Message:', e.data);
                    }};
                    ws.onerror = (e) => {{
                        reject({{status: 'error', error: e}});
                    }};
                    ws.onclose = () => {{
                        resolve({{status: 'closed'}});
                    }};
                    setTimeout(() => ws.close(), 5000);
                }})
            """)
            print(f"[WS] Direct connection result: {ws_test}")
        except Exception as e:
            print(f"[ERROR] Direct WS test failed: {e}")
        
        # Save results
        ws_file, ws_data = save_results()
        
        # Print sample of received messages
        if ws_messages_received:
            print(f"\n[7] Sample of {min(3, len(ws_messages_received))} received messages:")
            for msg in ws_messages_received[:3]:
                print(f"    {msg[:200]}..." if len(msg) > 200 else f"    {msg}")
        
        await context.close()
        print("\n[DONE] Capture complete!")

def handle_websocket(ws):
    """Handle WebSocket connection"""
    ws_info = {
        "url": ws.url,
        "protocol": ws.protocol if hasattr(ws, 'protocol') else "unknown",
        "postpone": ws.postpone if hasattr(ws, 'postpone') else False
    }
    ws_connections.append(ws_info)
    print(f"\n[WS] New WebSocket: {ws.url}")
    
    # Set up message handlers
    def on_message_sent(data):
        msg_str = str(data)
        ws_messages_sent.append(msg_str)
        print(f"[WS->] Sent: {msg_str[:100]}...")
    
    def on_message_received(data):
        msg_str = str(data)
        ws_messages_received.append(msg_str)
        print(f"[WS<-] Received: {msg_str[:100]}...")
    
    # These handlers would need to be attached to the actual WS object
    # Playwright's WebSocket handling is limited, but we capture the URL

def capture_request(request):
    """Capture network requests"""
    if "ws" in request.url or "socket" in request.url.lower():
        network_requests.append({
            "type": "websocket-related",
            "url": request.url,
            "method": request.method
        })

def capture_response(response):
    """Capture network responses"""
    url = response.url
    if "/ws/" in url or "socket" in url.lower() or "websocket" in url.lower():
        network_requests.append({
            "type": "websocket-response",
            "url": url,
            "status": response.status
        })

if __name__ == "__main__":
    asyncio.run(run())
