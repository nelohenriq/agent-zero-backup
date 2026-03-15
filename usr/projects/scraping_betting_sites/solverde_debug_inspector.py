import asyncio
import json
import time
import os
from playwright.async_api import async_playwright

OUTPUT_DIR = "/a0/usr/projects/scraping_betting_sites/processed_sports/json_backup"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        
        print("Navigating to Solverde sports page...")
        try:
            await page.goto("https://www.solverde.pt/pt-pt/apostas-desportivas", wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Navigation error: {e}")
            await browser.close()
            return
        
        print("Waiting for dynamic content...")
        await asyncio.sleep(10)
        
        # 1. Save full HTML
        print("Saving full HTML...")
        html = await page.content()
        filename = f"solverde_full_html_debug_{int(time.time())}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[SAVED] {filename}")
        
        # 2. Take screenshot
        print("Taking screenshot...")
        screenshot_path = os.path.join(OUTPUT_DIR, f"solverde_screenshot_{int(time.time())}.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"[SAVED] {screenshot_path}")
        
        # 3. Extract all class names
        print("Extracting all class names...")
        classes = await page.evaluate("""
            () => {
                const allElements = document.querySelectorAll('*');
                const classSet = new Set();
                allElements.forEach(el => {
                    if (el.className && typeof el.className === 'string') {
                        el.className.split(' ').forEach(c => {
                            if (c) classSet.add(c);
                        });
                    }
                });
                return Array.from(classSet).sort().join('\n');
            }
        """)
        
        class_file = os.path.join(OUTPUT_DIR, f"solverde_all_classes_{int(time.time())}.txt")
        with open(class_file, "w", encoding="utf-8") as f:
            f.write(classes)
        print(f"[SAVED] {class_file}")
        
        # 4. Find script tags with JSON
        print("Searching for JSON in script tags...")
        scripts = await page.evaluate("""
            () => {
                const allScripts = document.querySelectorAll('script');
                const jsonScripts = [];
                allScripts.forEach((script, idx) => {
                    if (script.textContent && script.textContent.includes('{') && script.textContent.includes('"')) {
                        jsonScripts.push({
                            index: idx,
                            length: script.textContent.length,
                            preview: script.textContent.substring(0, 200)
                        });
                    }
                });
                return jsonScripts;
            }
        """)
        
        scripts_file = os.path.join(OUTPUT_DIR, f"solverde_script_candidates_{int(time.time())}.json")
        with open(scripts_file, "w", encoding="utf-8") as f:
            json.dump(scripts, f, indent=2)
        print(f"[SAVED] {scripts_file}")
        
        # 5. Search for specific text to find elements
        print("Searching for 'La Liga' or 'Premier League' in text...")
        matches = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                const results = [];
                elements.forEach(el => {
                    if (el.textContent && (el.textContent.includes('La Liga') || el.textContent.includes('Premier League') || el.textContent.includes('Odds'))) {
                        results.push({
                            tag: el.tagName,
                            class: el.className,
                            text: el.textContent.substring(0, 100).replace(/\s+/g, ' ')
                        });
                    }
                });
                return results.slice(0, 20);
            }
        """)
        
        match_file = os.path.join(OUTPUT_DIR, f"solverde_text_matches_{int(time.time())}.json")
        with open(match_file, "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=2)
        print(f"[SAVED] {match_file}")
        
        await browser.close()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
