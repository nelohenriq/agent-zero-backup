import json
import os
import time
from playwright.sync_api import sync_playwright, WebSocket

OUTPUT_DIR = '/a0/usr/projects/scraping_betting_sites/processed_sports'
TARGET_URL = 'https://www.solverde.pt'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'solverde_ws_grpc_dump.json')

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_aggressive_capture():
    all_data = {
        "websockets": [],
        "grpc_responses": [],
        "http_responses": [],
        "errors": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-web-security'])
        context = browser.new_context()
        page = context.new_page()

        # Setup WebSocket listener
        page.on("websocket", lambda ws: handle_websocket(ws, all_data))
        
        # Setup HTTP response listener
        page.on("response", lambda resp: handle_response(resp, all_data))

        print(f"Navigating to {TARGET_URL}...")
        page.goto(TARGET_URL, wait_until='networkidle')
        time.sleep(3)

        print("Looking for 'Futebol' button...")
        try:
            # Try multiple selectors
            selector = page.query_selector('button:has-text("Futebol"), a:has-text("Futebol"), [data-testid*="futebol"], .nav-item:has-text("Futebol")')
            if not selector:
                # Fallback: look for any sport link
                selector = page.query_selector('a[href*="futebol"], a[href*="soccer"], a[href*="esportes"]')
            
            if selector:
                print("Clicking Futebol button...")
                selector.click()
                # Wait for network activity to settle
                page.wait_for_load_state('networkidle')
                time.sleep(5) # Give time for WS to connect and stream
            else:
                print("Futebol button not found, waiting anyway...")
                time.sleep(5)
        except Exception as e:
            print(f"Error clicking button: {e}")
            all_data["errors"].append(str(e))

        # Wait a bit more to catch delayed streams
        print("Waiting for potential streams...")
        time.sleep(10)

        # Save data
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"\nCapture complete. Saved to {OUTPUT_FILE}")
        print(f"WebSockets captured: {len(all_data['websockets'])}")
        print(f"gRPC responses: {len(all_data['grpc_responses'])}")
        print(f"HTTP responses: {len(all_data['http_responses'])}")

        browser.close()

def handle_websocket(ws, data):
    print(f"WebSocket opened: {ws.url}")
    ws_data = {"url": ws.url, "frames": []}
    
    def on_frame(frame):
        try:
            payload = frame.payload
            # Try to parse as JSON
            try:
                json_payload = json.loads(payload)
                ws_data["frames"].append({"type": "json", "data": json_payload})
            except json.JSONDecodeError:
                # Check if it looks like sports data (binary or text)
                if any(kw in str(payload).lower() for kw in ['odds', 'match', 'team', 'score', 'event']):
                    ws_data["frames"].append({"type": "text", "data": payload[:500]})
        except Exception as e:
            pass

    ws.on("framesent", lambda frame: on_frame(frame))
    ws.on("framereceived", lambda frame: on_frame(frame))
    ws.on("close", lambda: data["websockets"].append(ws_data))

def handle_response(resp, data):
    try:
        url = resp.url
        content_type = resp.headers.get('content-type', '').lower()
        status = resp.status
        
        # Skip images, css, fonts
        if any(x in content_type for x in ['image', 'css', 'font']):
            return

        # Check for gRPC (often application/grpc or similar)
        if 'grpc' in content_type:
            data["grpc_responses"].append({"url": url, "status": status, "type": "grpc"})
            return

        # Check for JSON
        if 'json' in content_type:
            try:
                body = resp.text()
                # Quick check for sports keywords
                if any(kw in body.lower() for kw in ['odds', 'match', 'team', 'score', 'event', 'fixture']):
                    data["http_responses"].append({
                        "url": url,
                        "status": status,
                        "type": "json",
                        "preview": body[:1000]
                    })
            except:
                pass
    except Exception as e:
        pass

if __name__ == "__main__":
    run_aggressive_capture()
