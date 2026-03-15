import asyncio
import json
from playwright.async_api import async_playwright

async def fetch_json_via_network_intercept():
    url = 'https://api.placard.bet/prefetch'
    output_file = 'placard_challenge_solved_data_v2.json'
    
    print(f"[INFO] Launching browser to intercept network request from {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        responses = []
        page.on('response', lambda response: responses.append(response))
        
        try:
            print("[INFO] Navigating to challenge page...")
            await page.goto(url, wait_until='networkidle')
            print("[INFO] Waiting for potential redirects and API calls...")
            await asyncio.sleep(5)
            
            print(f"[INFO] Final URL: {page.url}")
            print(f"[INFO] Captured {len(responses)} responses.")
            
            json_data = None
            json_url = None
            
            for resp in responses:
                try:
                    status = resp.status
                    if status == 200:
                        content_type = resp.headers.get('content-type', '')
                        if 'application/json' in content_type or 'json' in resp.url:
                            try:
                                data = await resp.json()
                                json_data = data
                                json_url = resp.url
                                print(f"[SUCCESS] Found JSON response from: {resp.url}")
                                break
                            except:
                                pass
                except Exception:
                    pass
            
            if json_data:
                print("[SUCCESS] JSON data captured!")
                with open(output_file, 'w') as f:
                    json.dump(json_data, f, indent=2)
                print(f"[SUCCESS] Data saved to {output_file}")
                print(f"[INFO] Root keys: {list(json_data.keys())}")
            else:
                print("[WARNING] No JSON response found in captured network traffic.")
                print("[INFO] Listing all captured response URLs:")
                for resp in responses:
                    print(f" - {resp.url} (Status: {resp.status}, Type: {resp.headers.get('content-type', 'unknown')})")
                    
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_json_via_network_intercept())
