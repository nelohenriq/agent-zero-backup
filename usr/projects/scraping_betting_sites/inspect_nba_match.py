from bs4 import BeautifulSoup
import os

html_file = "/a0/usr/projects/scraping_betting_sites/processed_sports/json_backup/solverde_correct_url_html_1772924711.html"

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

matches = soup.find_all('div', class_='ta-MatchEventCard')

print(f"Found {len(matches)} matches in HTML.")

for i, match in enumerate(matches):
    league_elem = match.find('div', class_='ta-headerTitle')
    league = league_elem.get_text(strip=True) if league_elem else "Unknown"
    
    teams = [t.get_text(strip=True) for t in match.find_all('div', class_='ta-participantName')]
    
    markets = []
    odds_btns = match.find_all('div', class_='ta-SelectionButtonView')
    for btn in odds_btns:
        market_name = btn.find('div', class_='ta-infoTextName')
        price = btn.find('div', class_='ta-price_text')
        if market_name and price:
            markets.append({
                "name": market_name.get_text(strip=True),
                "value": price.get_text(strip=True)
            })
    
    print(f"\n--- Match {i+1} ---")
    print(f"League: {league}")
    print(f"Teams: {teams}")
    print(f"Markets: {markets}")
    
    if not markets and "NBA" in league:
        print("\n[DEBUG] NBA Match found with NO markets. Saving full HTML snippet for analysis...")
        output_path = "/a0/usr/projects/scraping_betting_sites/nba_match_debug.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(str(match))
        print(f"Saved NBA match HTML to {output_path}")
        # Print first 500 chars of raw HTML
        print("Raw HTML snippet:")
        print(str(match)[:500] + "...")
