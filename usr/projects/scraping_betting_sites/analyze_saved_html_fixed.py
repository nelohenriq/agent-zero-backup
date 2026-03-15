import os
import json
from bs4 import BeautifulSoup

html_file = "/a0/usr/projects/scraping_betting_sites/processed_sports/json_backup/solverde_full_html_debug_1772924165.html"

if not os.path.exists(html_file):
    print(f"Error: {html_file} not found.")
    exit(1)

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 1. Find all unique class names
all_classes = set()
for tag in soup.find_all(True):
    if tag.get('class'):
        if isinstance(tag['class'], list):
            all_classes.update(tag['class'])
        else:
            all_classes.add(tag['class'])

sorted_classes = sorted(list(all_classes))
print(f"Found {len(sorted_classes)} unique class names.")
print("\n--- Sample of class names (first 50) ---")
print("\n".join(sorted_classes[:50]))

# 2. Search for specific text patterns to find betting cards
target_texts = ['La Liga', 'Premier League', 'Odds', 'Resultado Final', '2º P', '1X2']
matches = []

for text in target_texts:
    elements = soup.find_all(string=lambda t: t and text in t)
    for el in elements:
        parent = el.parent
        if parent:
            matches.append({
                "text_snippet": el.strip()[:100],
                "tag": parent.name,
                "class": parent.get('class', []),
                "id": parent.get('id', '')
            })

print(f"\n--- Found {len(matches)} elements matching target texts ---")
for m in matches[:15]:
    print(json.dumps(m, indent=2))

# 3. Find elements with class 'ta-SelectionButtonView' or similar
potential_odds = []
for tag in soup.find_all(True):
    tag_classes = tag.get('class', [])
    if any('Selection' in str(c) or 'Button' in str(c) or 'Price' in str(c) or 'Odds' in str(c) for c in tag_classes):
        potential_odds.append({
            "tag": tag.name,
            "class": tag_classes,
            "text": tag.get_text(strip=True)[:100]
        })

print(f"\n--- Found {len(potential_odds)} potential odds elements ---")
for m in potential_odds[:10]:
    print(json.dumps(m, indent=2))

# Save the analysis
analysis_file = "/a0/usr/projects/scraping_betting_sites/processed_sports/json_backup/solverde_html_analysis_fixed.json"
with open(analysis_file, 'w', encoding='utf-8') as f:
    json.dump({
        "total_classes": len(sorted_classes),
        "sample_classes": sorted_classes[:100],
        "text_matches": matches,
        "potential_odds_elements": potential_odds
    }, f, indent=2, ensure_ascii=False)

print(f"\nAnalysis saved to {analysis_file}")
