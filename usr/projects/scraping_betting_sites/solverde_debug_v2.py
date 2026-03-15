import json
import os
import time
from playwright.sync_api import sync_playwright

PROJECT_DIR = "/a0/usr/projects/scraping_betting_sites"
DEBUG_FILE = os.path.join(PROJECT_DIR, "processed_sports", "solverde_raw_debug.json")

def scrape_solverde_debug():
    print("🔍 Starting Solverde Debug Capture...")
    os.makedirs(os.path.dirname(DEBUG_FILE), exist_ok=True)
    captured = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        def handle_response(response):
            if response.status == 200 and "application/json" in response.headers.get("content-type", "").lower():
                try:
                    body = response.body()
                    if body and len(body) > 100:
                        text = body.decode("utf-8", errors="ignore")
                        try:
                            data = json.loads(text)
                            captured.append({
                                "url": response.url,
                                "size": len(text),
                                "data": data
                            })
                            print(f"📦 Captured JSON from: {response.url} (Size: {len(text)})")
                        except json.JSONDecodeError:
                            pass
                except Exception as e:
                    pass

        context.on("response", handle_response)
        
        page = context.new_page()
        try:
            print("🌐 Navigating to solverde.pt/futebol...")
            page.goto("https://www.solverde.pt/futebol", wait_until="networkidle", timeout=30000)
            print("✅ Page loaded. Waiting for content...")
            time.sleep(5)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error during navigation: {e}")
        finally:
            browser.close()
        
        with open(DEBUG_FILE, "w", encoding="utf-8") as f:
            json.dump(captured, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Total captured JSON responses: {len(captured)}")
        print(f"💾 Saved to: {DEBUG_FILE}")
        
        if captured:
            sorted_captured = sorted(captured, key=lambda x: x["size"], reverse=True)
            print("\n🔎 Top 5 largest responses (Top-level keys):")
            for i, item in enumerate(sorted_captured[:5]):
                url = item["url"]
                data = item["data"]
                keys = list(data.keys()) if isinstance(data, dict) else f"List of {len(data)} items"
                print(f"{i+1}. {url}")
                print(f"   Keys: {keys}")
                print()

if __name__ == "__main__":
    scrape_solverde_debug()
