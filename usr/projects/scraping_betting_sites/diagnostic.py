import asyncio
from playwright.async_api import async_playwright

async def diagnose():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        url = "https://www.placard.pt/apostas/inplay"
        print(f"[*] Navigating to {url}...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(10)

        # Take a screenshot to see what's on screen
        await page.screenshot(path="/a0/usr/projects/scraping_betting_sites/current_state.png", full_page=True)
        print("[*] Screenshot saved to current_state.png")

        # Check for iframes
        iframes = page.frames
        print(f"[*] Found {len(iframes)} frames.")

        # Dump all class names that might be relevant
        classes = await page.evaluate('''() => {
            const allElements = document.querySelectorAll('*');
            const classMap = {};
            allElements.forEach(el => {
                if (el.className && typeof el.className === 'string') {
                    el.className.split(' ').forEach(c => {
                        if (c) classMap[c] = (classMap[c] || 0) + 1;
                    });
                }
            });
            return Object.entries(classMap).sort((a,b) => b[1] - a[1]).slice(0, 50);
        }''')
        print("[*] Top 50 classes found:", classes)

        # Look for match-like text
        text_sample = await page.evaluate('''() => {
            return document.body.innerText.substring(0, 2000);
        }''')
        print("[*] Text Sample (first 2000 chars):\n", text_sample)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(diagnose())
