import json
import os
import glob

# Search all JSON files for socket.io or framegas data
json_files = glob.glob("processed_sports/*.json") + glob.glob("processed_sports/json_backup/*.json")

print(f"Searching {len(json_files)} files for socket.io/framegas data...")

found_data = []
for jf in json_files:
    try:
        with open(jf, 'r', errors='ignore') as f:
            content = f.read()
            if 'framegas.com' in content and ('socket' in content.lower() or 'event' in content.lower() or 'odds' in content.lower()):
                found_data.append(jf)
                print(f"\n*** Found framegas reference: {jf}")
                idx = content.find('framegas')
                print(content[max(0,idx-20):idx+300])
    except Exception as e:
        print(f"Error {jf}: {e}")

# Check for any WebSocket frame data with actual messages
print("\n\n=== CHECKING FOR WEBSOCKET FRAME DATA ===")

ws_files = [f for f in json_files if 'ws' in f.lower() or 'frame' in f.lower() or 'socket' in f.lower()]
print(f"Found {len(ws_files)} potential WebSocket files: {ws_files[:5]}")

for wf in ws_files[:8]:
    try:
        with open(wf) as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            print(f"\n{wf}:")
            print(f" Keys: {list(data.keys())[:10]}")
        
        for key in ['frames', 'messages', 'sent', 'received', 'data', 'events', 'ws_messages', 'socket_messages']:
            if key in data:
                val = data[key]
                if isinstance(val, list) and len(val) > 0:
                    print(f" {key}: {len(val)} items")
                    print(f" Sample: {str(val[0])[:500]}")
    except Exception as e:
        print(f"Error {wf}: {e}")

# Look at raw API responses with sports content
print("\n\n=== EXAMINING RAW API RESPONSE CONTENT ===")

for f in ['processed_sports/solverde_extended_60s_20260307_174905.json',
          'processed_sports/solverde_api_capture_full_20260307_001048.json']:
    if os.path.exists(f):
        with open(f) as fp:
            data = json.load(fp)
        
        if 'api_responses' in data:
            for resp in data['api_responses'][:15]:
                url = resp.get('url', '')
                status = resp.get('status', '')
                if status == 200:
                    body = resp.get('body', '')
                    if body and len(body) > 100 and 'sport' in url.lower():
                        print(f"\n*** {url} ***")
                        print(body[:2000])
