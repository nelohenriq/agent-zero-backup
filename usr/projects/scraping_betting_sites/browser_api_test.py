import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        print("Navigating to Placard Soccer...")
        await page.goto("https://www.placard.pt/apostas/sports/soccer", wait_until="networkidle")
        
        # Get a match ID from the page links
        match_link = await page.wait_for_selector("a[href*='/events/']", timeout=10000)
        match_href = await match_link.get_attribute("href")
        mid = match_href.split("/")[-1]
        print(f"Found Match ID: {mid}")

        # Navigate to match to establish full context
        await page.goto(f"https://www.placard.pt/apostas/sports/soccer/events/{mid}", wait_until="networkidle")

        # Define JS fetcher
        fetch_js = """
        async (url, method='GET', body=null) => {
            const options = {
                method: method,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            };
            if (body) options.body = JSON.stringify(body);
            try {
                const response = await fetch(url, options);
                const data = await response.json();
                return { status: response.status, data: data };
            } catch (e) {
                return { error: e.message };
            }
        }
        """

        # Test Event Details
        details_url = f"https://sportswidget-cdn.placard.pt/api/events/{mid}?locale=pt_PT"
        print(f"Testing Details API: {details_url}")
        details_res = await page.evaluate(f"({fetch_js})('{details_url}')")
        print(f"Details Status: {details_res.get('status')}")
        
        if details_res.get('status') == 200:
            event_data = details_res['data']
            market_ids = [str(m['id']) for m in event_data.get('marketLines', {}).values()]
            print(f"Found {len(market_ids)} market IDs.")

            # Test Markets Multi
            if market_ids:
                multi_url = "https://sportswidget-cdn.placard.pt/api/markets/multi?locale=pt_PT"
                print(f"Testing Markets Multi: {multi_url}")
                multi_res = await page.evaluate(f"({fetch_js})('{multi_url}', 'POST', {json.dumps(market_ids)})")
                print(f"Multi Status: {multi_res.get('status')}")
                if multi_res.get('status') == 200:
                    print("Successfully fetched odds data!")
                    # Print a small sample
                    print(json.dumps(multi_res['data'][:1], indent=2))
        else:
            print(f"Details Error/Fail: {details_res}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
