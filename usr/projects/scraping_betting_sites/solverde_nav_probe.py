import json
import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = 'https://www.solverde.pt'
SPORTS_PATHS = [
    '/desportos',
    '/futebol',
    '/apostas',
    '/desportos/futebol',
    '/apostas/futebol',
    '/sports',
    '/football'
]
OUTPUT_FILE = '/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_nav_probe.json'

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def run_probe():
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Collect network responses
        responses = []
        page.on('response', lambda response: responses.append({
            'url': response.url,
            'status': response.status,
            'headers': dict(response.headers),
            'content_type': response.headers.get('content-type', ''),
            'size': len(response.body()) if response.status == 200 else 0
        }))
        
        print(f"Testing base URL: {BASE_URL}")
        try:
            page.goto(BASE_URL, wait_until='networkidle')
            time.sleep(5)
            
            # Inspect Nav
            nav_links = []
            try:
                nav_elements = page.query_selector_all('nav a, .nav-item a, [role="navigation"] a')
                for el in nav_elements:
                    href = el.get_attribute('href')
                    text = el.inner_text().strip()
                    if href and ('sport' in href.lower() or 'futebol' in href.lower() or 'desporto' in href.lower() or 'aposta' in href.lower()):
                        nav_links.append({'href': href, 'text': text})
            except Exception as e:
                nav_links.append({'error': str(e)})
            
            results.append({
                'url': BASE_URL,
                'status': 'success',
                'nav_links': nav_links,
                'network_count': len(responses)
            })
            print(f"  Found {len(nav_links)} relevant nav links.")
            
        except Exception as e:
            results.append({'url': BASE_URL, 'status': 'error', 'error': str(e)})
        
        # Test specific paths
        for path in SPORTS_PATHS:
            url = BASE_URL + path
            print(f"Testing: {url}")
            try:
                # Reset responses for this test
                current_responses = []
                # We can't easily reset the listener, so we'll just append and filter later
                # But for now, let's just try to load and see if it redirects or 404s
                page.goto(url, wait_until='domcontentloaded', timeout=10000)
                
                # Check for redirects or 404s
                status = page.status
                content = page.content()
                
                results.append({
                    'url': url,
                    'status': 'success' if status < 400 else f'HTTP {status}',
                    'content_length': len(content),
                    'title': page.title()
                })
                print(f"  Status: {status}, Title: {page.title()}")
                
            except Exception as e:
                results.append({'url': url, 'status': 'error', 'error': str(e)})
                print(f"  Error: {e}")
        
        # Save results
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nProbe results saved to {OUTPUT_FILE}")
        
        # Print summary
        print("\n=== SUMMARY ===")
        for r in results:
            if r.get('status') == 'success':
                print(f"OK: {r['url']} (Links: {len(r.get('nav_links', []))})")
            else:
                print(f"FAIL: {r['url']} ({r.get('status', 'Unknown')})")
        
        browser.close()

if __name__ == "__main__":
    run_probe()
