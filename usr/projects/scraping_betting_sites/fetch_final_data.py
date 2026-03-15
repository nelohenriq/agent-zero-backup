import json
import time
from playwright.sync_api import sync_playwright, Request, Response

def main():
    print("[INFO] Starting Playwright to solve challenge and fetch data...")
    
    # Store captured responses
    captured_responses = []
    challenge_token = None
    final_data = None
    
    def on_response(response: Response):
        try:
            # Check if response is JSON
            if 'application/json' in response.headers.get('content-type', ''):
                try:
                    data = response.json()
                    print(f"[INFO] Captured JSON from: {response.url}")
                    captured_responses.append({"url": response.url, "data": data})
                    
                    # Check if this is the challenge response (has 'tc')
                    if isinstance(data, dict) and 'tc' in data:
                        challenge_token = data['tc']
                        print(f"[INFO] Found challenge token: {challenge_token[:20]}...")
                        
                    # Check if this is the final data (has 'eventGroups')
                    if isinstance(data, dict) and 'eventGroups' in data:
                        final_data = data
                        print("[SUCCESS] Found final sports data!")
                except:
                    pass
        except Exception as e:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        # Set up response interception
        page.on("response", on_response)
        
        # Navigate to the challenge page
        # Based on previous logs, the redirect was to http://ww38.api.placard.bet/prefetch
        # But the original challenge page was likely https://api.placard.bet/prefetch or similar
        # Let's try the main API endpoint first
        target_url = "https://api.placard.bet/prefetch"
        print(f"[INFO] Navigating to {target_url}...")
        
        try:
            page.goto(target_url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"[WARNING] Navigation error: {e}")
        
        # Wait a bit for any async redirects or challenges to resolve
        time.sleep(5)
        
        # If we have a challenge token, try to request the data again with it
        # The challenge response had 'ra' with 'req' and 'jsonp'. 
        # Often the token is passed as a query param or header.
        if challenge_token and not final_data:
            print(f"[INFO] Challenge token found. Attempting to fetch data with token...")
            
            # Try adding token as query param
            # Sometimes the 'req' from 'ra' is the session ID
            # Let's try the most common pattern: ?token=...
            token_url = f"{target_url}?token={challenge_token}"
            print(f"[INFO] Requesting: {token_url}")
            
            try:
                page.goto(token_url, wait_until="networkidle", timeout=30000)
                time.sleep(3)
            except Exception as e:
                print(f"[WARNING] Token request error: {e}")
            
            # Also try the 'req' value from 'ra' if available
            # We need to extract it from the last challenge response
            for resp in reversed(captured_responses):
                if 'tc' in resp['data']:
                    ra_data = resp['data'].get('ra', {})
                    req_val = ra_data.get('req')
                    if req_val:
                        # Try as header or param
                        # Try as header 'x-challenge-token' or similar
                        page.goto(f"{target_url}?req={req_val}", wait_until="networkidle", timeout=30000)
                        time.sleep(3)
                        break
        
        # Check if we got the data
        if final_data:
            output_file = "placard_final_sports_data.json"
            with open(output_file, 'w') as f:
                json.dump(final_data, f, indent=2)
            print(f"[SUCCESS] Data saved to {output_file}")
            print(f"[INFO] Sports count: {len(final_data.get('sportsMetaInformation', []))}")
            print(f"[INFO] Event groups count: {len(final_data.get('eventGroups', []))}")
        else:
            # Save all captured responses for debugging
            debug_file = "placard_debug_responses.json"
            with open(debug_file, 'w') as f:
                json.dump(captured_responses, f, indent=2)
            print(f"[WARNING] Final data not found. Saved debug responses to {debug_file}")
            print("[INFO] Inspecting captured responses for clues...")
            for resp in captured_responses:
                if 'tc' in resp['data']:
                    print(f"  - Challenge response from {resp['url']}")
                    print(f"    ra.req: {resp['data'].get('ra', {}).get('req')}")
        
        browser.close()

if __name__ == "__main__":
    main()
