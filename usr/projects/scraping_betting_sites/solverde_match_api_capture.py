#!/usr/bin/env python3
"""
Solverde.pt Live Match Data Capture Script
Uses Playwright to intercept API calls when viewing football betting
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def capture_solverde_api():
    """Capture API responses from Solverde.pt football section"""
    intercepted_data = []
    
    print("Starting Solverde capture...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track all network requests
        async def handle_request(request):
            record = {
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type,
                'timestamp': datetime.now().isoformat()
            }
            intercepted_data.append(record)
        
        # Track responses
        async def handle_response(response):
            for record in intercepted_data:
                if record['url'] == response.url:
                    record['status'] = response.status
                    try:
                        body = await response.text()
                        record['body_length'] = len(body)
                        record['body_type'] = 'html' if '<html' in body.lower() else 'json' if body.strip().startswith(('{', '[')) else 'other'
                        if 'futebol' in response.url.lower() or 'sport' in response.url.lower() or 'match' in response.url.lower():
                            record['sports_related'] = True
                    except Exception as e:
                        record['body_error'] = str(e)
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        try:
            print("Navigating to solverde.pt...")
            await page.goto('https://www.solverde.pt', wait_until='networkidle', timeout=30000)
            
            # Wait for page to load
            await page.wait_for_timeout(2000)
            
            print("Looking for Football button...")
            
            # Try multiple selectors for "Futebol"
            selectors = [
                'text=Futebol',
                'a:has-text("Futebol")',
                'button:has-text("Futebol")',
                '[class*="futebol"]',
                'xpath=//a[contains(@class, "futebol")]'
            ]
            
            clicked = False
            for sel in selectors:
                try:
                    element = await page.query_selector(sel)
                    if element:
                        await element.click()
                        print(f"Clicked element using selector: {sel}")
                        clicked = True
                        break
                except Exception as e:
                    continue
            
            if not clicked:
                print("Could not click Football button - page may have changed")
                
            # Wait for content to load
            print("Waiting for content...")
            await page.wait_for_timeout(3000)
            
            # Get page HTML for analysis
            html = await page.content()
            print(f"Page HTML length: {len(html)} chars")
            
            # Final wait
            print("Final wait for delayed requests...")
            await asyncio.sleep(3)
            
            # Save results
            output_path = f"solverde_match_api_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(intercepted_data, f, indent=2, ensure_ascii=False)
            
            print(f"\nCapture complete!")
            print(f"Intercepted {len(intercepted_data)} responses")
            print(f"Saved to: {output_path}")
            
            # Summary
            if intercepted_data:
                print("\nTop URLs intercepted:")
                for i, record in enumerate(intercepted_data[:10]):
                    status = record.get('status', 'pending')
                    print(f" {i+1}. {record['url']} ({status})")
            else:
                print("\nWARNING: No responses intercepted!")
                
        except Exception as e:
            print(f"Error during capture: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print("\nBrowser will remain open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_solverde_api())
