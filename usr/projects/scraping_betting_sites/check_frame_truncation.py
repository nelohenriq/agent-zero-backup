import json

with open('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_ws_v8_20260307_164139.json') as f:
 data = json.load(f)

recv = data.get('frames_received', [])

# Check frame 5 raw content
print("=== FRAME 5 RAW ===")
frame_5 = recv[5]['text']
print(f"Frame 5 length: {len(frame_5)}")
print(f"Frame 5 content:\n{frame_5}")
print("\n=== Checking content-length headers ===")
for i, frame in enumerate(recv[:15]):
    txt = frame.get('text', '')
    # Look for content-length
    if 'content-length' in txt.lower():
        for line in txt.split('\n'):
            if 'content-length' in line.lower():
                print(f"Frame {i}: {line.strip()}")
    print(f"Frame {i}: actual length = {len(txt)}")
