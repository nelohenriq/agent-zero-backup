import requests
from bs4 import BeautifulSoup
import re
import json

# Download main page
print("Downloading Solverde.pt main page...")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

try:
    resp = requests.get('https://www.solverde.pt/apostas/desportivas', headers=headers, timeout=30)
    print(f"Page status: {resp.status_code}")
    print(f"Page size: {len(resp.text)} chars")
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Extract all script tags
    scripts = soup.find_all('script')
    print(f"\nFound {len(scripts)} script tags")
    
    # Get src attributes
    script_urls = []
    for s in scripts:
        src = s.get('src', '')
        if src:
            script_urls.append(src)
    
    print("\n=== Script URLs ===")
    for url in script_urls:
        print(url)
    
    # Save for later analysis
    with open('script_urls.json', 'w') as f:
        json.dump(script_urls, f, indent=2)
    
    # Also look for inline scripts with API calls
    print("\n=== Looking for API patterns in inline scripts ===")
    for s in scripts:
        if not s.get('src'):  # inline scripts
            content = s.string or ''
            if 'fetch' in content or 'axios' in content or '$.ajax' in content or 'wss://' in content or 'ws://' in content:
                print("--- Found inline script with potential API calls ---")
                # Extract relevant parts
                for pattern in [r'fetch\(["\']([^"\']+)', r'axios\(["\']([^"\']+)', r'wss://[^\s"\']+', r'ws://[^\s"\']+', r'/api/[^\s"\']+']:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"Pattern {pattern}: {matches[:5]}")
                        
except Exception as e:
    print(f"Error: {e}")

