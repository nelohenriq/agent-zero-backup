import asyncio
import json
import os
from playwright.async_api import async_playwright

async def solve_challenge():
    url = "https://api.placard.bet/prefetch?tr_uuid=20260307-1028-09ca-b6fe-af091c0fc2d8&fp=-7"
    output_file = "placard_solved_data_playwright.json"
    
    print(f"Starting browser to solve challenge for: {url}")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        # Store responses
        responses = {}
        
        # Intercept network requests
        async def handle_response(response):
            if "prefetch" in response.url and response.status == 200:
                try:
                    text = await response.text()
                    # Check if it's JSON
                    if text.strip().startswith('{') or text.strip().startswith('['):
                        responses[response.url] = json.loads(text)
                        print(f"[INTERCEPTED] Found JSON response at: {response.url}")
                except:
                    pass
        
        page.on("response", handle_response)
        
        try:
            # Navigate
            print("Navigating...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait a bit more for any JS redirects or async loads
            await asyncio.sleep(5)
            
            # Check if the page itself is JSON (unlikely but possible)
            content_type = await page.evaluate("() => document.contentType")
            page_content = await page.content()
            
            if content_type and 'application/json' in content_type:
                print("Page content is JSON.")
                try:
                    data = json.loads(page_content)
                    responses["page_content"] = data
                except:
                    pass
            else:
                # Check if the page is a redirect or challenge page
                # If we have intercepted responses, use the last one
                if responses:
                    print(f"Found {len(responses)} intercepted responses.")
                    # Try to find the one with eventGroups
                    for u, data in responses.items():
                        if isinstance(data, dict) and 'eventGroups' in data:
                            print("SUCCESS: Found data with 'eventGroups'!")
                            with open(output_file, 'w') as f:
                                json.dump(data, f, indent=2)
                            print(f"Saved to {output_file}")
                            return
                    
                    # If no specific match, save the last one
                    last_url = list(responses.keys())[-1]
                    print(f"Saving last intercepted response from {last_url}")
                    with open(output_file, 'w') as f:
                        json.dump(responses[last_url], f, indent=2)
                else:
                    print("No JSON responses intercepted. Saving page HTML for inspection.")
                    with open("placard_challenge_page.html", "w") as f:
                        f.write(page_content)
                    print("Saved page HTML to placard_challenge_page.html")
                    
        except Exception as e:
            print(f"Error during navigation: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(solve_challenge())
