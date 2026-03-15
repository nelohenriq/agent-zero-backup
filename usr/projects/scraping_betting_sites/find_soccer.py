import json

with open('processed_sports/solverde_ws_live_20260307_161713.json', 'r') as f:
    data = json.load(f)

frames = data.get('websocket_frames', [])

# Find messages after frame 36 that contain soccer/football data
soccer_data = []
for i, f in enumerate(frames):
    if i < 36:
        continue
    raw = f.get('data', '')
    if 'soccer' in raw.lower() and len(raw) > 500 and 'items' in raw:
        soccer_data.append((i, raw[:3000]))

print(f"Soccer response frames: {len(soccer_data)}")

for idx, content in soccer_data[:2]:
    print(f"\n=== Frame {idx} ===")
    lines = content.split('\n')
    for line in lines[:15]:
        print(line)
    print("...")
    start = content.find('{"id"')
    if start > 0:
        print(content[start:start+800])
