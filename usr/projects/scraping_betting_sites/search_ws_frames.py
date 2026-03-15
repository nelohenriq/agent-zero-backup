import json

with open('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_ws_v8_20260307_164139.json') as f:
    data = json.load(f)

recv = data.get('frames_received', [])
sent = data.get('frames_sent', [])

keywords = ['sport', 'futebol', 'football', 'soccer', 'match', 'odds', 'league', 'competition', 'team']

print("=== SEARCHING RECEIVED FRAMES ===")
for i, fr in enumerate(recv):
    txt = fr.get('text', '')
    lower_txt = txt.lower()
    for kw in keywords:
        if kw in lower_txt:
            print(f"\nFrame {i} contains '{kw}':")
            print(f"Length: {len(txt)}")
            print(f"Preview: {txt[:800]}")
            if len(txt) > 800:
                print(f"...{txt[-300:]}")
            break

print("\n=== SEARCHING SENT FRAMES ===")
for i, fr in enumerate(sent):
    txt = fr.get('text', '')
    lower_txt = txt.lower()
    for kw in keywords:
        if kw in lower_txt:
            print(f"\nSent Frame {i} contains '{kw}': {txt[:500]}")
            break
