#!/usr/bin/env python3
"""Analyze JavaScript files for API patterns and test discovered endpoints."""

import re
import json
import requests
from pathlib import Path

PROJECT_DIR = Path('/a0/usr/projects/scraping_betting_sites')

def test_endpoint(url, method='GET', headers=None):
    """Test an API endpoint and return results."""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'pt-PT,pt;q=0.9,en;q=0.8',
            'Referer': 'https://www.solverde.pt/apostas/desportivas',
        }
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, timeout=15)
        else:
            resp = requests.post(url, headers=headers, timeout=15)
        return {
            'url': url,
            'status': resp.status_code,
            'content_type': resp.headers.get('Content-Type', ''),
            'content_length': len(resp.content),
            'preview': resp.text[:500] if resp.text else ''
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}

def find_js_patterns(html):
    """Find API patterns in HTML source."""
    patterns_found = {}
    
    # Simple pattern searches
    api_urls = re.findall(r'https?://[^\s"<>]+(?:api|odds|live|sports|widget)[^\s"<>]*', html, re.I)
    ws_urls = re.findall(r'wss?://[^\s"<>]+', html)
    
    if api_urls:
        patterns_found['api_urls'] = list(set(api_urls))
    if ws_urls:
        patterns_found['ws_urls'] = list(set(ws_urls))
    
    return patterns_found

def main():
    print("=" * 60)
    print("SOLVERDE.JS - API Pattern Analyzer")
    print("=" * 60)
    
    # 1. Load the HTML and find patterns
    print("\n1. Analyzing HTML for API patterns...")
    html_file = PROJECT_DIR / 'processed_sports/solverde_full_source.html'
    if not html_file.exists():
        html_file = PROJECT_DIR / 'processed_sports/solverde_full_source_v2.html'
    
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        
        patterns = find_js_patterns(html)
        
        print(f"   Found {len(patterns.get('api_urls', []))} API URLs")
        print(f"   Found {len(patterns.get('ws_urls', []))} WebSocket URLs")
        
        # Show them
        for url in patterns.get('api_urls', [])[:10]:
            print(f"   - {url[:80]}")
        for url in patterns.get('ws_urls', [])[:5]:
            print(f"   - {url}")
        
        # Save patterns
        with open(PROJECT_DIR / 'processed_sports/js_api_patterns.json', 'w') as f:
            json.dump(patterns, f, indent=2)
    
    # 2. Test specific known endpoints
    print("\n2. Testing known endpoints...")
    
    endpoints_to_test = [
        # FrameAPI / Socket.io
        'https://openapi.framegas.com/socket.io/?EIO=4&transport=polling',
        'https://openapi.framegas.com/socket.io/?EIO=4&transport=websocket',
        
        # Sportswidget API
        'https://sportswidget.solverde.pt/config',
        'https://sportswidget.solverde.pt/api/sports',
        'https://sportswidget.solverde.pt/api/odds',
        'https://sportswidget.solverde.pt/api/live',
        'https://sportswidget.solverde.pt/api/events',
        
        # Solverde main API
        'https://www.solverde.pt/api/sportsbook/sports',
        'https://www.solverde.pt/api/sportsbook/odds',
        'https://www.solverde.pt/api/sportsbook/events',
        'https://www.solverde.pt/api/sportsbook/live',
        
        # Odds API variants
        'https://www.solverde.pt/apostas/desportivas',
        'https://www.solverde.pt/sportsbook',
    ]
    
    results = []
    for url in endpoints_to_test:
        result = test_endpoint(url)
        results.append(result)
        if 'error' not in result:
            status_str = f"[{result['status']}]"
            clen = f"{result['content_length']} bytes"
            preview = result['preview'][:100] if result['preview'] else ''
            print(f" {status_str:6} {clen:10} {url[:50]}...")
            
            # Check for sports data
            if preview:
                preview_lower = preview.lower()
                if any(k in preview_lower for k in ['sport', 'match', 'team', 'odds', 'event', 'futebol']):
                    print(f"        ^^^ CONTAINS SPORTS DATA!")
        else:
            print(f" [ERROR] {url[:50]}... - {result['error'][:40]}")
    
    # Save results
    with open(PROJECT_DIR / 'processed_sports/api_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # 3. Search captured data for sports keywords
    print("\n3. Searching captured data for sports keywords...")
    
    sports_keywords = ['match', 'team', 'odds', 'event', 'futebol', 'football', 
                       'liga', 'porto', 'benfica', 'sporting', 'braga', 'game']
    
    capture_files = list(PROJECT_DIR.glob('processed_sports/*.json'))
    
    found_files = []
    for cf in capture_files[:20]:
        try:
            with open(cf, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            found = [kw for kw in sports_keywords if kw in content]
            if found:
                found_files.append((cf.name, found[:5]))
                print(f" {cf.name}: {', '.join(found[:5])}")
        except:
            pass
    
    # 4. Try Playwright to extract DOM data
    print("\n4. Running Playwright to extract DOM data...")
    
    playwright_script = '''
from playwright.sync_api import sync_playwright
import json
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate and wait
        page.goto('https://www.solverde.pt/apostas/desportivas', wait_until="networkidle", timeout=60000)
        time.sleep(5)
        
        # Extract page content
        content = page.content()
        
        # Try to find odds in DOM
        odds_elements = page.query_selector_all('[class*="odd"], [class*="odds"], [class*="bet"]')
        
        # Extract text with sports keywords
        sports_keywords = ['futebol', 'futbol', 'football', 'odds', 'liga', 'porto', 'benfica']
        
        # Get body text
        body_text = page.evaluate("""
            () => {
                return document.body.innerText.substring(0, 50000);
            }
        """)
        
        browser.close()
        
        return {
            'content_length': len(content),
            'body_text': body_text,
            'odds_elements_count': len(odds_elements)
        }

if __name__ == '__main__':
    result = run()
    print(json.dumps(result, indent=2))
'''
    
    with open(PROJECT_DIR / 'playwright_extract.py', 'w') as f:
        f.write(playwright_script)
    
    print("Script created. Running...")
    
import subprocess
result = subprocess.run(
    ['python3', str(PROJECT_DIR / 'playwright_extract.py')],
    capture_output=True,
    text=True,
    timeout=90
)
print(result.stdout)
if result.stderr:
    print(f"Errors: {result.stderr[:500]}")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)

