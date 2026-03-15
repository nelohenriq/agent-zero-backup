import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    # 1. Load market IDs from fresh_prefetch.json
    with open('/a0/usr/projects/scraping_betting_sites/fresh_prefetch.json', 'r') as f:
        data = json.load(f)
    
    soccer_event = next((e for e in data.get('events', []) if e.get('sportId') == 'soccer'), None)
    if not soccer_event:
        print("No soccer event found in prefetch.")
        return

    market_ids = [str(m['id']) for m in soccer_event.get('marketLines', {}).values()]
    print(f"Testing Event: {soccer_event.get('name')} (ID: {soccer_event['id']})")
    print(f"Market IDs: {market_ids}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        
        # Need to be on the domain for cookies/session
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")

        multi_url = "https://sportswidget-cdn.placard.pt/api/markets/multi?locale=pt_PT"
        
        fetch_script = """
        async (url, ids) => {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Referer': 'https://www.placard.pt/'
                },
                body: JSON.stringify(ids)
            });
            if (!response.ok) return { error: response.status };
            return await response.json();
        }
        """

        result = await page.evaluate(f"({fetch_script})('{multi_url}', {json.dumps(market_ids)})")
        
        if "error" in result:
            print(f"Error fetching odds: {result['error']}")
        else:
            print("Successfully fetched odds!")
            print(json.dumps(result[:1], indent=2)) # Print first market odd as sample

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
