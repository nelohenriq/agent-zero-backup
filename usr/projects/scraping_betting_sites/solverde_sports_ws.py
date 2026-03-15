from playwright.sync_api import sync_playwright
import json
import time

print('Starting Solverde sports capture with WebSocket monitoring...')
results = {'timestamp': time.time(), 'ws_frames': [], 'dom_data': {}, 'errors': []}

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Track WebSockets
        ws_messages = []
        def on_ws(ws):
            print(f'WS connected: {ws.url}')
            ws_messages.append({'event': 'connected', 'url': ws.url})
        page.on('websocket', on_ws)
        
        # Track requests
        requests = []
        def on_req(r):
            if 'api' in r.url.lower() or 'sports' in r.url.lower() or 'bet' in r.url.lower():
                requests.append(r.url)
        page.on('request', on_req)
        
        # Go directly to sports betting URL
        print('Loading sports betting page...')
        page.goto('https://www.solverde.pt/apostas/desportivas', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        print(f'Requests captured: {len(requests)}')
        
        # Look for football content
        texts = page.evaluate('''() => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let node, texts = [];
            const kw = ['porto', 'benfica', 'sporting', 'liga', 'futebol', 'over', 'under', '1x2', 'empate', 'vitória'];
            while (node = walker.nextNode()) {
                const t = node.textContent.trim().toLowerCase();
                if (t.length > 5 && kw.some(k => t.includes(k))) texts.push(node.textContent.trim().substring(0,100));
            }
            return [...new Set(texts)].slice(0,50);
        }''')
        
        results['dom_data']['betting_texts'] = texts
        results['requests'] = requests[:20]
        results['ws_frames'] = ws_messages
        
        browser.close()
        print(f'Found {len(texts)} betting texts')
        print(f'WebSocket messages: {len(ws_messages)}')

except Exception as e:
    results['errors'].append(str(e))
    print(f'Error: {e}')

with open('solverde_sports_capture.json', 'w') as f:
    json.dump(results, f, indent=2)

print('Saved solverde_sports_capture.json')
print('Betting texts:', results['dom_data'].get('betting_texts', [])[:10])
print('API requests:', results.get('requests', []))
