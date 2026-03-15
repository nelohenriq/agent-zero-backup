import json

with open('processed_sports/solverde_ws_live_20260307_161713.json', 'r') as f:
 data = json.load(f)

frames = data.get('websocket_frames', [])
print(f"Total frames: {len(frames)}")

# Look for any frames with event data
interesting = []
for i, f in enumerate(frames):
 raw = f.get('data', '')
 # Look for patterns indicating match data
 if any(x in raw.lower() for x in ['"event"', '"competition"', '"team"', '"match"']) and len(raw) > 400:
 interesting.append((i, raw[:2500]))

print(f"Interesting frames: {len(interesting)}")

for idx, content in interesting[:3]:
 print(f"\n=== Frame {idx} ===")
 start = content.find('{"')
 if start >= 0:
 print(content[start:start+1200])
