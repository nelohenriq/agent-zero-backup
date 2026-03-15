#!/usr/bin/env python3
"""
Solverde Scraper with WebSocket Capture
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import re

http_intercepted = []
ws_frames = []
ws_connections = []

def is_betting_related(text):
    """Check if content is betting-related"""
    keywords = ['odds', 'bet', 'futebol', 'football', 'soccer', 'match', 
                'liga', 'copa', 'campeonato', 'resultado', 'preco', 'cuota']
    text_lower = str(text).lower()
    return any(kw in text_lower for kw in keywords)

async def handle_response(response):
    """Capture HTTP responses"""
    try:
        url = response.url
        status = response.status
        
        # Try to get response body
        body = ""
        try:
            if response.status < 400:
                body = await response.text()
        except:
            pass
        
        entry = {
            'url': url,
            'status': status,
            'betting_related': is_betting_related(url + body),
            'body_preview': body[:500] if body else "",
            'timestamp': datetime.now().isoformat()
        }
        http_intercepted.append(entry)
        
    except Exception as e:
        pass

async def handle_websocket(ws):
    """Handle new WebSocket connections"""
    ws_connections.append({
        'url': ws.url,
        'timestamp': datetime.now().isoformat()
    })
    print(f"[WS] Connected: {ws.url}")
    
    # Listen for frames
    async def on_frame(frame):
        frame_data = {
            'type': frame.type,
            'payload': frame.text if hasattr(frame, 'text') else str(frame),
            'timestamp': datetime.now().isoformat(),
            'betting_related': False
        }
        
        payload = frame_data['payload']
        if payload:
            frame_data['betting_related'] = is_betting_related(payload)
            frame_data['payload_preview'] = payload[:200]
        
        ws_frames.append(frame_data)
        
        if frame_data['betting_related']:
            print(f"[WS BETTING] {payload[:100]}...")
    
    ws.on('frame', on_frame)

async def click_futebol(page):
    """Click on Futebol section"""
    # Try multiple selectors
    selectors = [
        'text=Futebol',
        'a:has-text("Futebol")',
        'button:has-text("Futebol")',
        '[class*="futebol"]',
        '[data-sport="futebol"]',
        '#futebol',
    ]
    
    for sel in selectors:
        try:
            element = await page.query_selector(sel)
            if element:
                await element.click()
                print(f"[2] Clicked Futebol with selector: {sel}")
                await asyncio.sleep(2)
                return True
        except:
            continue
    
    print("[2] Warning: Could not click Futebol button")
    return False

async def main():
    print("=" * 60)
    print("Solverde WebSocket Capture Script")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context()
        page = await context.new_page()
        
        # Set up handlers
        page.on("response", handle_response)
        
        # Try to capture WebSockets via console
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}") if "ws" in msg.text.lower() or "websocket" in msg.text.lower() else None)
        
        print("\n[1] Opening Solverde.pt...")
        try:
            await page.goto("https://www.solverde.pt", timeout=30000)
            print("[1] Page loaded")
        except Exception as e:
            print(f"[1] Failed: {e}")
            return
        
        # Wait a bit
        await asyncio.sleep(3)
        
        # Click Futebol
        print("\n[2] Clicking Futebol...")
        await click_futebol(page)
        
        # Wait for data
        print("\n[3] Waiting for data (20 seconds)...")
        for i in range(10):
            await asyncio.sleep(2)
            print(f"[3] Waited {(i+1)*2}s - WS frames: {len(ws_frames)}, HTTP: {len(http_intercepted)}")
        
        # Save captures
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if http_intercepted:
            http_file = f"solverde_ws_http_{timestamp}.json"
            with open(http_file, "w", encoding="utf-8") as f:
                json.dump(http_intercepted, f, indent=2)
            print(f"\n[Saved] {len(http_intercepted)} HTTP responses to {http_file}")
        
        if ws_frames:
            ws_file = f"solverde_ws_frames_{timestamp}.json"
            with open(ws_file, "w", encoding="utf-8") as f:
                json.dump(ws_frames, f, indent=2)
            print(f"[Saved] {len(ws_frames)} WebSocket frames to {ws_file}")
        
        # Summary
        print("\n" + "=" * 60)
        print("CAPTURE SUMMARY")
        print("=" * 60)
        print(f"HTTP Responses: {len(http_intercepted)}")
        print(f"WebSocket Connections: {len(ws_connections)}")
        print(f"WebSocket Frames: {len(ws_frames)}")
        
        # Find betting data
        betting_http = [r for r in http_intercepted if r.get('betting_related')]
        betting_ws = [f for f in ws_frames if f.get('betting_related')]
        
        print(f"\nBetting-related HTTP: {len(betting_http)}")
        print(f"Betting-related WS: {len(betting_ws)}")
        
        await browser.close()
        print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())
