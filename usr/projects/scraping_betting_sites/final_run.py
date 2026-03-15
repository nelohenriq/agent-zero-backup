import asyncio
import csv
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def scrape():
    csv_path = "/a0/usr/projects/scraping_betting_sites/placard_data.csv"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        print("[*] Opening Live Section...")
        await page.goto("https://www.placard.pt/apostas/inplay", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(15)
        
        try: await page.click("button:has-text('Aceitar')", timeout=5000)
        except: pass

        text = await page.evaluate("() => document.body.innerText")
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        matches = []
        for i in range(len(lines)):
            if re.search(r'\d+\s*[:\-]\s*\d+', lines[i]):
                score = lines[i]
                window = lines[max(0, i-10):min(len(lines), i+15)]
                teams = [l for l in window if len(l) > 3 and not any(c.isdigit() for c in l) and l.upper() not in ["RESULTADOS", "AO VIVO", "MAIS", "MENOS"]]
                odds = [l.replace(',', '.') for l in window if re.match(r'^[0-9]+[.,][0-9]{2}$', l)]

                if len(teams) >= 2 and len(odds) >= 2:
                    name = f"{teams[0]} vs {teams[1]}"
                    if not any(m['name'] == name for m in matches):
                        matches.append({'name': name, 'score': score, 'odds': (odds[:3] + ["N/A"]*3)[:3]})

        if matches:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Match Name", "Score", "Odds 1", "Odds X", "Odds 2"])
                for m in matches:
                    row = [datetime.now().strftime("%H:%M:%S"), m['name'], m['score']] + m['odds']
                    writer.writerow(row)
                    print(f"[+] CAPTURED: {m['name']} | {m['score']} | Odds: {m['odds']}")
        else: print("[!] No matches found.")
        await browser.close()

if __name__ == '__main__': asyncio.run(scrape())
