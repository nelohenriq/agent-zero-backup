
import asyncio
import json
import os
import time
from playwright.async_api import async_playwright

OUTPUT_DIR = '/a0/usr/projects/scraping_betting_sites/processed_sports/json_backup'
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        captured = []

        async def handle_response(response):
            try:
                url = response.url
                status = response.status
                if status == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'json' in content_type or 'application/json' in content_type:
                        try:
                            text = await response.text()
                            if len(text) < 100000:
                                data = json.loads(text)
                                text_str = str(data).lower()
                                keywords = ['odds', 'selection', 'team', 'match', 'participant', 'price', 'win', 'draw', 'lose', 'fixture', 'market', 'line']
                                if any(kw in text_str for kw in keywords):
                                    filename = f"solverde_live_odds_{int(time.time())}.json"
                                    filepath = os.path.join(OUTPUT_DIR, filename)
                                    with open(filepath, 'w', encoding='utf-8') as f:
                                        json.dump({'url': url, 'status': status, 'headers': dict(response.headers), 'data': data}, f, indent=2, ensure_ascii=False)
                                    print(f"[SAVED] {filename} from {url}")
                                    captured.append(filename)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                pass

        page.on('response', handle_response)

        print("Navigating to Solverde sports page...")
        await page.goto('https://www.solverde.pt/pt-pt/apostas-desportivas', wait_until='networkidle', timeout=60000)

        print("Waiting for dynamic content (SSE/Long-polling)...")
        await asyncio.sleep(20)

        print("Closing browser...")
        await browser.close()

        print(f"\nCapture complete. Saved {len(captured)} files.")
        print(f"Check {OUTPUT_DIR} for results.")

if __name__ == '__main__':
    asyncio.run(main())
