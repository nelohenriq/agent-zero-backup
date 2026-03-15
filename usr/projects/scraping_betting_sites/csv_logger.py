import asyncio
import csv
import re
import os
import time
from datetime import datetime
from playwright.async_api import async_playwright

def parse_live_text(text):
    """Parses the raw text stream for live match patterns based on verified diagnostic dump."""
    matches = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Heuristic for teams: lines > 3 chars with no digits.
    # Score is usually digits and a colon or hyphen.
    # Odds are decimal numbers like 2.20.
    i = 0
    while i < len(lines) - 10:
        line = lines[i]
        # Potential team 1 (no digits, not menu text)
        if len(line) > 3 and not any(c.isdigit() for c in line) and line.upper() not in ['REGISTAR', 'INICIAR', 'APOSTAS', 'AO VIVO', 'DESPORTOS', 'MAIS', 'MENOS']:
            next_line = lines[i+1]
            # Potential team 2
            if len(next_line) > 3 and not any(c.isdigit() for c in next_line) and next_line != line:
                match_name = f"{line} vs {next_line}"
                score = "0 - 0"
                odds = []
                
                # Look in a window of 30 lines for score and odds
                window = lines[i:i+35]
                window_text = " ".join(window)
                
                # Look for score (e.g., "2 : 1" or "1 - 1")
                s_match = re.search(r'(\d+)\s*[:\-]\s*(\d+)', window_text)
                if s_match:
                    score = f"{s_match.group(1)} - {s_match.group(2)}"
                
                # Look for decimal odds (dot or comma)
                for l in window:
                    if re.match(r'^[0-9]+[.,][0-9]{2}$', l):
                        odds.append(l.replace(',', '.'))
                
                if len(odds) >= 2:
                    matches.append({
                        'name': match_name,
                        'score': score,
                        'odds': (odds[:3] + ["N/A"]*3)[:3]
                    })
                    i += 2 # Skip the teams we just processed
                    continue
        i += 1
    return matches

async def run_logger():
    csv_path = "/a0/usr/projects/scraping_betting_sites/placard_data.csv"
    
    async with async_playwright() as p:
        print("[*] Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        # Initialize/Clear CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Match Name", "Score", "Odds 1", "Odds X", "Odds 2"])

        print("[*] Navigating to verified Live URL: https://www.placard.pt/apostas/inplay")
        await page.goto("https://www.placard.pt/apostas/inplay", wait_until="networkidle", timeout=60000)
        
        print("[*] Waiting 15s for dynamic data to populate...")
        await asyncio.sleep(15)

        # Dismiss cookies if present
        try:
            await page.click("button:has-text('Aceitar')", timeout=5000)
            print("[*] Cookies accepted.")
        except:
            pass

        print("[*] Scraping and logging for 60 seconds...")
        start_time = time.time()
        while time.time() - start_time < 60:
            # Get full text representing current visible state
            text = await page.evaluate("() => document.body.innerText")
            results = parse_live_text(text)
            
            if results:
                ts = datetime.now().strftime("%H:%M:%S")
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for r in results:
                        writer.writerow([ts, r['name'], r['score']] + r['odds'])
                        print(f"[CAPTURED {ts}] {r['name']} | Score: {r['score']} | Odds: {r['odds']}")
                    f.flush()
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No data detected in UI text, scrolling to trigger load...")
                await page.mouse.wheel(0, 500)

            await asyncio.sleep(15)
            
        await browser.close()
        print("[*] Scraping session finished.")

if __name__ == "__main__":
    asyncio.run(run_logger())
