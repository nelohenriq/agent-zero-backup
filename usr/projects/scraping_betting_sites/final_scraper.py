import asyncio
import csv
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def run():
    csv_path = "/a0/usr/projects/scraping_betting_sites/placard_data.csv"
    async with async_playwright() as p:
        print("[*] Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()

        print("[*] Navigating to In-Play section...")
        await page.goto("https://www.placard.pt/apostas/inplay", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(15)

        # Handle cookies
        try: await page.click("button:has-text('Aceitar')", timeout=5000)
        except: pass

        print("[*] Extracting and parsing visible text...")
        text = await page.evaluate("() => document.body.innerText")
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        matches = []
        # Contextual parser: Find scores and look for teams/odds nearby
        for i in range(len(lines)):
            # Look for score pattern (e.g., "2 : 1", "1 - 1", or "0-0")
            if re.search(r'\d+\s*[:\-]\s*\d+', lines[i]):
                score = lines[i]
                # Search a window around the score (-10 to +15 lines)
                window = lines[max(0, i-10):min(len(lines), i+15)]
                
                # Extract teams (lines with only letters, > 3 chars)
                teams = [l for l in window if len(l) > 3 and not any(c.isdigit() for c in l) and l.upper() not in ["RESULTADOS", "AO VIVO", "MAIS", "MENOS", "TOTAL"]]
                # Extract odds (decimal numbers)
                odds = [l.replace(',', '.') for l in window if re.match(r'^[0-9]+[.,][0-9]{2}$', l)]

                if len(teams) >= 2 and len(odds) >= 2:
                    match_name = f"{teams[0]} vs {teams[1]}"
                    if not any(m['name'] == match_name for m in matches):
                        matches.append({
                            'name': match_name,
                            'score': score,
                            'odds': (odds[:3] + ["N/A"]*3)[:3]
                        })

        if matches:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Match Name", "Score", "Odds 1", "Odds X", "Odds 2"])
                for m in matches:
                    writer.writerow([ts, m['name'], m['score']] + m['odds'])
                    print(f"[+] CAPTURED: {m['name']} | {m['score']} | Odds: {m['odds']}")
            print(f"[*] Successfully logged {len(matches)} matches.")
        else:
            print("[!] No matches found. Site may have no live events or layout changed.")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
