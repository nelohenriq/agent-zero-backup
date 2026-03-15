"""Solverde WebSocket Live Capture Script
Captures WebSocket frames for live odds data"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

ws_log = []
ws_connections = []

async def run():
    global ws_log, ws_connections
    
    print("Starting Solverde WebSocket capture...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track WebSocket frames
        def handle_ws(ws):
            ws_connections.append({
                'url': ws.url,
                'time': datetime.now().isoformat()
            })
            print(f"[WS CONNECTED] {ws.url}")
            
            # Listen for messages
            ws.on('framesent', lambda f: ws_log.append({
                'direction': 'sent',
                'time': datetime.now().isoformat(),
                'data': f.text if hasattr(f, 'text') else str(f)
            }))
            ws.on('framereceived', lambda f: ws_log.append({
                'direction': 'received',
                'time': datetime.now().isoformat(),
                'data': f.text if hasattr(f, 'text') else str(f)
            }))
        
        page.on('websocket', handle_ws)
        
        # Also track all network requests
        network_log = []
        page.on('request', lambda r: network_log.append({
            'url': r.url,
            'method': r.method,
            'time': datetime.now().isoformat()
        }))
        
        print("Navigating to Solverde.pt...")
        try:
            await page.goto('https://www.solverde.pt', timeout=30000)
            await page.wait_for_load_state('networkidle')
            print("Page loaded")
        except Exception as e:
            print(f"Initial load error: {e}")
        
        # Wait for any WebSocket connections
        await asyncio.sleep(3)
        
        # Click on Futebol
        print("Clicking Futebol...")
        try:
            # Try multiple selectors
            selectors = [
                'text=Futebol',
                'a[href*="futebol"]', 
                'button:has-text("Futebol")',
                'span:has-text("Futebol")',
                '[class*="futebol"]',
            ]
            for sel in selectors:
                try:
                    await page.click(sel, timeout=2000)
                    print(f"Clicked: {sel}")
                    break
                except:
                    continue
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Click error: {e}")
        
        # Look for live odds section
        print("Looking for live section...")
        try:
            await page.click('text=Ao Vivo', timeout=3000)
            print("Clicked Ao Vivo")
        except:
            pass
        
        await asyncio.sleep(5)
        
        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'websocket_connections': ws_connections,
            'websocket_frames': ws_log,
            'network_count': len(network_log),
            'page_title': await page.title()
        }
        
        # Filter network for API endpoints
        api_endpoints = [r for r in network_log if 'api' in r['url'].lower() or 'ws' in r['url'].lower()]
        results['api_endpoints'] = api_endpoints
        
        # Save to file
        fname = f"processed_sports/solverde_ws_live_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(fname, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n=== RESULTS ===")
        print(f"WebSocket connections: {len(ws_connections)}")
        print(f"WebSocket frames: {len(ws_log)}")
        print(f"Total network requests: {len(network_log)}")
        print(f"API endpoints found: {len(api_endpoints)}")
        
        if ws_connections:
            print("\nWebSocket URLs:")
            for c in ws_connections:
                print(f"  {c['url']}")
        
        if ws_log:
            print(f"\nFirst 3 frames:")
            for frame in ws_log[:3]:
                print(f"  [{frame['direction']}] {frame['data'][:100]}...")
        
        await browser.close()
        return results

if __name__ == '__main__':
    asyncio.run(run())
