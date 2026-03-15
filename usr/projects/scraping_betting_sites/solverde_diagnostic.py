import json
import os
import time
from playwright.sync_api import sync_playwright

TARGET_URL = 'https://www.solverde.pt'
OUTPUT_FILE = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_diagnostic.json'

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def run_diagnostic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to {TARGET_URL}...")
        page.goto(TARGET_URL, wait_until='networkidle')
        
        # Wait longer for dynamic content
        print("Waiting 10 seconds for dynamic content...")
        time.sleep(10)
        
        # Get full HTML
        html = page.content()
        
        # Check for iframes
        iframes = page.frames
        iframe_info = []
        for i, frame in enumerate(iframes):
            try:
                iframe_info.append({
                    "index": i,
                    "url": frame.url,
                    "name": frame.name if hasattr(frame, 'name') else "",
                    "locator": str(frame.locator("body"))
                })
            except:
                iframe_info.append({"index": i, "url": frame.url, "error": "Could not access frame"})
        
        # Try to find 'Futebol' button/link
        selectors = [
            'button:has-text("Futebol")',
            'a:has-text("Futebol")',
            '[aria-label*="Futebol"]',
            '[title*="Futebol"]',
            '[data-testid*="futebol"]',
            'a[href*="futebol"]',
            'a[href*="Futebol"]',
            'nav a:has-text("Futebol")',
            'div.nav-item:has-text("Futebol")',
            'li:has-text("Futebol") a',
            'span:has-text("Futebol")'
        ]
        
        found_elements = []
        for selector in selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    found_elements.append({
                        "selector": selector,
                        "count": len(elements),
                        "text": [el.inner_text() for el in elements[:5]]
                    })
            except Exception as e:
                found_elements.append({"selector": selector, "error": str(e)})
        
        # Also check for any link containing 'futebol' (case insensitive) in href or text
        all_links = page.query_selector_all('a')
        futebol_links = []
        for link in all_links:
            try:
                href = link.get_attribute('href') or ''
                text = link.inner_text() or ''
                if 'futebol' in href.lower() or 'futebol' in text.lower():
                    futebol_links.append({
                        "href": href,
                        "text": text,
                        "class": link.get_attribute('class')
                    })
            except:
                pass
        
        # Save diagnostic data
        diagnostic_data = {
            "html_length": len(html),
            "html_sample": html[:5000], # First 5000 chars
            "iframes": iframe_info,
            "selectors_tested": found_elements,
            "futebol_links_found": futebol_links,
            "all_links_count": len(all_links)
        }
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(diagnostic_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nDiagnostic saved to {OUTPUT_FILE}")
        print(f"Iframes found: {len(iframe_info)}")
        print(f"Futebol links found: {len(futebol_links)}")
        if futebol_links:
            print("Sample Futebol link:", futebol_links[0])
        if found_elements:
            print("Selectors that matched:")
            for item in found_elements:
                if 'count' in item and item['count'] > 0:
                    print(f"  {item['selector']}: {item['count']} matches")
        
        browser.close()

if __name__ == "__main__":
    run_diagnostic()
