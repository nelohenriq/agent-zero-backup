import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def main():
    output = {
        "timestamp": datetime.now().isoformat(),
        "url": "https://www.solverde.pt/apostas/desportivas",
        "wait_time": 60,
        "network_requests": [],
        "websocket_urls": [],
        "api_responses": [],
        "page_content_length": 0,
        "errors": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track WebSockets
        ws_urls = []
        ws_messages = []
        
        def handle_request(request):
            if "api" in request.url.lower() or "odds" in request.url.lower() or "sport" in request.url.lower():
                output["network_requests"].append({
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type
                })
        
        page.on("request", handle_request)
        
        # Track responses
        async def handle_response(response):
            url = response.url
            if "api" in url.lower() or "sport" in url.lower() or "bet" in url.lower():
                try:
                    body = await response.text()
                    if len(body) < 50000:  # Skip huge responses
                        output["api_responses"].append({
                            "url": url,
                            "status": response.status,
                            "body_preview": body[:2000]
                        })
                except Exception as e:
                    output["errors"].append(f"Response error: {str(e)[:100]}")
        
        page.on("response", handle_response)
        
        print("Navigating to Solverde... (waiting 60s for data load)")
        try:
            await page.goto("https://www.solverde.pt/apostas/desportivas", timeout=30000)
            print(f"Page loaded. Waiting 60 seconds for live data...")
            
            # Extended wait for data
            await asyncio.sleep(60)
            
            # Get page content
            content = await page.content()
            output["page_content_length"] = len(content)
            
            # Extract URLs from page
            urls = await page.evaluate("""
                () => {
                    const urls = [];
                    // Check all script src
                    document.querySelectorAll('script[src]').forEach(s => urls.push(s.src));
                    // Check all link href
                    document.querySelectorAll('link[href]').forEach(l => urls.push(l.href));
                    // Check fetch/axios calls in window
                    for (let key in window) {
                        if (key.includes('api') || key.includes('API')) {
                            urls.push('window.' + key);
                        }
                    }
                    return urls;
                }
            """)
            output["extracted_urls"] = urls
            
            print(f"Page content length: {len(content)}")
            print(f"Captured {len(output['network_requests'])} network requests")
            print(f"Captured {len(output['api_responses'])} API responses")
            
        except Exception as e:
            output["errors"].append(str(e)[:200])
            print(f"Error: {e}")
        
        await browser.close()
    
    # Save results
    with open(f"processed_sports/solverde_extended_60s_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\\n=== CAPTURE SUMMARY ===")
    print(f"Network requests: {len(output['network_requests'])}")
    print(f"API responses: {len(output['api_responses'])}")
    print(f"Page content: {output['page_content_length']} bytes")
    
    # Show API URLs found
    print("\\n=== API URLs FOUND ===")
    for req in output["network_requests"][:15]:
        print(f"  {req['method']} {req['url'][:80]}")

asyncio.run(main())
