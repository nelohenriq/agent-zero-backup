import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports"

ws_data = {"connections": [], "frames_sent": [], "frames_received": []}

async def run():
    global ws_data
    
    print("=== Solverde WS Capture v7 (Full Frame Capture) ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        # More comprehensive WS handler
        page.on("websocket", lambda ws: (
            print(f"\n[WS OPEN] {ws.url}"),
            ws_data["connections"].append({"url": ws.url, "time": datetime.now().isoformat()}),
            ws.on("framesent", lambda f: (
                print(f"[WS ->] {f.text[:100] if f.text else str(f)[:100]}"),
                ws_data["frames_sent"].append({"time": datetime.now().isoformat(), "text": f.text[:500] if f.text else str(f)[:500]})
            )),
            ws.on("framereceived", lambda f: (
                print(f"[WS <-] {f.text[:100] if f.text else str(f)[:100]}"),
                ws_data["frames_received"].append({"time": datetime.now().isoformat(), "text": f.text[:500] if f.text else str(f)[:500]})
            ))
        ))
        
        # Navigate and wait
        print("Loading solverde.pt...")
        await page.goto("https://www.solverde.pt", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)
        
        # Try different selectors for "Futebol"
        print("\nSearching for sports menu...")
        selectors = ["text=Futebol", "a:has-text('Futebol')", "button:has-text('Futebol')", "[class*='futebol']", "text=Desportos"]
        for sel in selectors:
            try:
                await page.click(sel, timeout=2000)
                print(f"Clicked: {sel}")
                break
            except:
                continue
        
        # Wait for live data
        print("\nWaiting for live odds...")
        await page.wait_for_timeout(20000)
        
        # Try clicking on live games section
        print("\nLooking for live games...")
        try:
            await page.click("text=Ao Vivo", timeout=3000)
            print("Clicked Ao Vivo")
        except: pass
        
        try:
            await page.click("text=Live", timeout=3000)
            print("Clicked Live")
        except: pass
        
        await page.wait_for_timeout(10000)
        
        # Save
        ws_data["capture_end"] = datetime.now().isoformat()
        ws_data["page_url"] = page.url
        
        out_file = os.path.join(OUTPUT_DIR, f"solverde_ws_v7_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(out_file, "w") as f:
            json.dump(ws_data, f, indent=2)
        
        print(f"\n=== RESULTS ===")
        print(f"Connections: {len(ws_data['connections'])}")
        for c in ws_data['connections']:
            print(f"  {c['url']}")
        print(f"\nFrames sent: {len(ws_data['frames_sent'])}")
        print(f"Frames recv: {len(ws_data['frames_received'])}")
        
        # Show sample frames
        if ws_data['frames_received']:
            print("\nSample received frame:")
            print(ws_data['frames_received'][0]['text'][:300])
        
        await browser.close()

asyncio.run(run())
print("\nDone!")
