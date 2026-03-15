import json
import os
import re
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = '/a0/usr/projects/scraping_betting_sites/processed_sports'
TARGET_URL = 'https://www.solverde.pt'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'solverde_final_capture.json')

def run_comprehensive_capture():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_data = {
        "html_source": "",
        "network_responses": [],
        "embedded_json_blocks": [],
        "script_tags_count": 0
    }
    
    keywords = ['match', 'odds', 'team', 'fixture', 'event', 'score', 'home', 'away', 'market', 'bet', 'eventid', 'sportid']
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to {TARGET_URL}...")
        page.goto(TARGET_URL, wait_until='networkidle')
        time.sleep(2)
        
        intercepted_responses = []
        
        def handle_response(response):
            try:
                url = response.url
                status = response.status
                content_type = response.headers.get('content-type', '').lower()
                
                # Capture all responses that are not images, css, or fonts
                if 'image' not in content_type and 'css' not in content_type and 'font' not in content_type:
                    try:
                        text = response.text()
                        # Limit size to avoid memory issues
                        if len(text) < 50000:
                            intercepted_responses.append({
                                "url": url,
                                "status": status,
                                "content_type": content_type,
                                "size": len(text),
                                "preview": text[:500]
                            })
                    except Exception as e:
                        pass
            except Exception:
                pass
        
        page.on('response', handle_response)
        
        print("Looking for 'Futebol' button...")
        selectors = ["text=Futebol", "a:has-text('Futebol')", "button:has-text('Futebol')"]
        clicked = False
        
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element.count() > 0:
                    print(f"Clicking '{selector}'...")
                    element.click()
                    clicked = True
                    break
            except Exception:
                continue
        
        if not clicked:
            print("'Futebol' button not found. Trying 'Esportes'...")
            try:
                element = page.locator("text=Esportes").first
                if element.count() > 0:
                    element.click()
                    clicked = True
            except Exception:
                pass
        
        if clicked:
            print("Waiting for data to load...")
            page.wait_for_timeout(5000)
            page.wait_for_selector('body', state='attached')
        
        # Get full HTML
        print("Saving HTML source...")
        all_data["html_source"] = page.content()
        
        # Scan HTML for script tags with JSON
        print("Scanning HTML for embedded JSON...")
        script_tags = re.findall(r'<script[^>]*>([\s\S]*?)</script>', all_data["html_source"])
        all_data["script_tags_count"] = len(script_tags)
        
        for i, script in enumerate(script_tags):
            # Try to find JSON-like structures
            if '{' in script and '}' in script:
                # Heuristic: look for JSON objects with sports keywords
                # We will try to extract valid JSON objects from the script content
                depth = 0
                start = -1
                for j, char in enumerate(script):
                    if char == '{':
                        if depth == 0:
                            start = j
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0 and start != -1:
                            candidate = script[start:j+1]
                            try:
                                data = json.loads(candidate)
                                # Check if it contains any keywords
                                data_str = json.dumps(data).lower()
                                if any(kw in data_str for kw in keywords):
                                    all_data["embedded_json_blocks"].append({
                                        "index": len(all_data["embedded_json_blocks"]),
                                        "source": "script_tag",
                                        "data": data,
                                        "preview": candidate[:200]
                                    })
                            except json.JSONDecodeError:
                                pass
                            start = -1
        
        # Save network responses
        all_data["network_responses"] = intercepted_responses
        
        # Analyze results
        print(f"\nCapture complete.")
        print(f"Script tags found: {all_data['script_tags_count']}")
        print(f"Network responses captured: {len(all_data['network_responses'])}")
        print(f"Embedded JSON blocks found: {len(all_data['embedded_json_blocks'])}")
        
        # Save to file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved comprehensive data to {OUTPUT_FILE}")
        
        # Print summaries of found data
        if all_data["embedded_json_blocks"]:
            print("\n--- Found Embedded JSON Blocks ---")
            for block in all_data["embedded_json_blocks"]:
                print(f"Block {block['index']}: {block['preview'][:100]}...")
        
        if all_data["network_responses"]:
            print("\n--- Found Network Responses (Potential Data) ---")
            for resp in all_data["network_responses"]:
                if any(kw in resp['preview'].lower() for kw in keywords):
                    print(f"URL: {resp['url']}")
                    print(f"Type: {resp['content_type']}")
                    print(f"Preview: {resp['preview'][:100]}...")
                    print("---")
        
        browser.close()

if __name__ == "__main__":
    run_comprehensive_capture()
