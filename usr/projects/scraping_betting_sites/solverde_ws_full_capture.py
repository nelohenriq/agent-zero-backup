"""
Solverde WebSocket Full Frame Capture
Captures complete WebSocket frames without truncation
"""
import asyncio
import json
from playwright.async_api import async_playwright

CAPTURE_FILE = "/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_ws_full_v2.json"

async def capture():
    ws_connections = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture WebSocket connections
        async def on_request(request):
            if 'websocket' in request.url.lower():
                print(f"WS Request: {request.url}")
                ws_connections.append({
                    'url': request.url,
                    'method': request.method
                })
        
        page.on('request', on_request)
        
        # Navigate to Solverde
        print("Navigating to solverde.pt...")
        await page.goto("https://www.solverde.pt/apostas/desportivas", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Click on Futebol - using different locator approach
        try:
            football_link = page.locator('a').filter(has_text="Futebol").first
            await football_link.click(timeout=5000)
            print("Clicked Futebol")
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Click failed: {e}")
        
        # Inject JS to capture WebSocket frames with FULL content
        capture_script = """
        () => {
            window.wsFramesSent = [];
            window.wsFramesReceived = [];
            
            const OriginalWebSocket = window.WebSocket;
            window.WebSocket = function(url, protocols) {
                console.log('[WS CONNECT]', url);
                const ws = protocols ? new OriginalWebSocket(url, protocols) : new OriginalWebSocket(url);
                
                const originalSend = ws.send;
                ws.send = function(data) {
                    const frameData = {
                        timestamp: new Date().toISOString(),
                        url: url,
                        data: data,
                        dataLength: data.length,
                        type: typeof data
                    };
                    window.wsFramesSent.push(frameData);
                    console.log('[WS SEND]', data.length, 'bytes');
                    return originalSend.apply(this, arguments);
                };
                
                ws.onmessage = function(event) {
                    const frameData = {
                        timestamp: new Date().toISOString(),
                        url: url,
                        data: event.data,
                        dataLength: event.data.length,
                        type: event.data.constructor.name
                    };
                    window.wsFramesReceived.push(frameData);
                    console.log('[WS RECV]', event.data.length, 'bytes');
                };
                
                return ws;
            };
            console.log('WebSocket capture injected');
        }
        """
        await page.evaluate(capture_script)
        
        # Wait for data to come in
        print("Waiting for WebSocket data...")
        await page.wait_for_timeout(10000)
        
        # Extract captured frames - NO TRUNCATION
        ws_data = await page.evaluate("""
        () => ({
            sent: window.wsFramesSent || [],
            received: window.wsFramesReceived || []
        })
        """)
        
        print(f"Captured: {len(ws_data['sent'])} sent, {len(ws_data['received'])} received")
        
        # Save full capture
        capture = {
            'timestamp': '2026-03-07T17:05:00Z',
            'url': 'https://www.solverde.pt/apostas/desportivas',
            'ws_connections': ws_connections,
            'frames_sent': ws_data['sent'],
            'frames_received': ws_data['received']
        }
        
        with open(CAPTURE_FILE, 'w') as f:
            json.dump(capture, f, indent=2)
        
        print(f"Saved to {CAPTURE_FILE}")
        
        # Show frame sizes
        for i, frame in enumerate(ws_data['received'][:5]):
            print(f"Frame {i}: {frame.get('dataLength', 'unknown')} bytes")
        
        await browser.close()

asyncio.run(capture())
