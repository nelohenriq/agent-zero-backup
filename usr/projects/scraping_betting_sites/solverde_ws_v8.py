
import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports"

ws_data = {"connections": [], "frames_sent": [], "frames_received": []}

async def run():
    global ws_data
    
    print("=== Solverde WS Capture v8 ===")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # WS handler
        def on_ws(ws):
            print(f"\n[WS OPEN] {ws.url}")
            ws_data["connections"].append({"url": ws.url, "time": datetime.now().isoformat()})
            
            def on_sent(frame):
                text = str(frame)[:200]
                print(f"[WS ->] {text}")
                ws_data["frames_sent"].append({"time": datetime.now().isoformat(), "text": text})
            
            def on_received(frame):
                text = str(frame)[:500]
                print(f"[WS <-] {text}")
                ws_data["frames_received"].append({"time": datetime.now().isoformat(), "text": text})
            
            ws.on("framesent", on_sent)
            ws.on("framereceived", on_received)
        
        page.on("websocket", on_ws)
        
        print("Loading solverde.pt...")
        await page.goto("https://www.solverde.pt", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)
        
        # Click Desportos/Futebol
        for sel in ["text=Desportos", "text=Futebol", "a:has-text('Desportos')", "button:has-text('Desportos')"]:
            try:
                await page.click(sel, timeout=2000)
                print(f"Clicked: {sel}")
                break
            except:
                continue
        
        await page.wait_for_timeout(5000)
        
        # Click Ao Vivo (Live)
        for sel in ["text=Ao Vivo", "text=Live", "button:has-text('Ao Vivo')"]:
            try:
                await page.click(sel, timeout=2000)
                print(f"Clicked: {sel}")
                break
            except:
                continue
        
        await page.wait_for_timeout(15000)
        
        # Save results
        ws_data["capture_end"] = datetime.now().isoformat()
        ws_data["page_url"] = page.url
        
        out_file = os.path.join(OUTPUT_DIR, f"solverde_ws_v8_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(out_file, "w") as f:
            json.dump(ws_data, f, indent=2)
        
        print(f"\n=== RESULTS ===")
        print(f"Connections: {len(ws_data['connections'])}")
        for c in ws_data['connections']:
            print(f"  {c['url']}")
        print(f"\nFrames sent: {len(ws_data['frames_sent'])}")
        print(f"Frames received: {len(ws_data['frames_received'])}")
        
        if ws_data['frames_received']:
            print("\n--- Sample received frames ---")
            for i, frame in enumerate(ws_data['frames_received'][:3]):
                print(f"\nFrame {i+1}: {frame['text'][:400]}")
        
        await browser.close()

asyncio.run(run())
print("\nDone!")
