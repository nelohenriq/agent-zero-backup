import asyncio
import json
import os
from playwright.async_api import async_playwright, Response
from datetime import datetime

BASE_URL = "https://solverde.pt"
OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"solverde_playwright_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

captured_responses = []

def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

async def handle_response(response: Response):
    url = response.url
    status = response.status
    
    # Filter for relevant API endpoints
    if 'mpc-prod' in url or '/api/' in url or '/sports/' in url or 'events' in url:
        try:
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                body = await response.text()
                if body and len(body) < 50 * 1024 * 1024:
                    captured_responses.append({
                        "url": url,
                        "status": status,
                        "method": response.request.method,
                        "headers": dict(response.headers),
                        "body": body,
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"Captured: {url} (Status: {status}, Size: {len(body)})")
        except Exception as e:
            print(f"Error processing response {url}: {e}")

async def main():
    ensure_dir()
    print(f"Starting Playwright capture for {BASE_URL}...")
    print(f"Output will be saved to: {OUTPUT_FILE}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="pt-PT",
            timezone_id="Europe/Lisbon"
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)
        
        page = await context.new_page()
        page.on("response", handle_response)
        
        try:
            print(f"Navigating to {BASE_URL}...")
            await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
            print("Waiting for dynamic content to load...")
            await asyncio.sleep(5)
            
            # Try to click sports section
            try:
                sports_link = await page.query_selector("a[href*='esportes'], a[href*='desportos'], .sports-nav, .menu-item-sports")
                if sports_link:
                    print("Clicking on sports section...")
                    await sports_link.click()
                    await asyncio.sleep(5)
            except Exception as e:
                print(f"Could not click sports link: {e}")
            
            print(f"Capture complete. Found {len(captured_responses)} relevant responses.")
        except Exception as e:
            print(f"Error during navigation: {e}")
        finally:
            await browser.close()
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(captured_responses, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(captured_responses)} responses to {OUTPUT_FILE}")
        
        sports_keys = {'events', 'competitions', 'sports', 'data', 'matches', 'odds', 'leagues'}
        found_count = 0
        for i, resp in enumerate(captured_responses):
            body = resp.get('body', '')
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    keys = set(data.keys())
                    if keys & sports_keys:
                        print(f"[MATCH] Response {i}: {resp['url']}")
                        print(f" Keys: {list(keys)}")
                        found_count += 1
                elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    first_keys = set(data[0].keys())
                    if first_keys & sports_keys:
                        print(f"[MATCH] Response {i}: {resp['url']}")
                        print(f" Keys: {list(first_keys)}")
                        found_count += 1
            except:
                pass
        
        print(f"Total matches with sports structure: {found_count}")

if __name__ == "__main__":
    asyncio.run(main())
