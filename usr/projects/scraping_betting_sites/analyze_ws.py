import json

with open('processed_sports/solverde_ws_live_20260307_161713.json') as f:
    data = json.load(f)

ws_frames = data.get('websocket_frames', [])
print(f'Total WS frames: {len(ws_frames)}')

sports_keywords = ['odds', 'match', 'team', 'score', 'gol', 'porto', 'benfica', 'sport', 'futebol', 'liga', 'mercado', 'aposta', 'jogo']

print('\n=== Frames with sports data ===')
for frame in ws_frames:
    data_str = str(frame.get('data', '')).lower()
    for kw in sports_keywords:
        if kw in data_str:
            print(f"\n[{frame['direction']}] {frame['data'][:500]}")
            break
