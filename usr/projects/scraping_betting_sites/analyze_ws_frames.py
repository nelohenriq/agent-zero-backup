import json

with open('processed_sports/solverde_ws_live_20260307_161713.json') as f:
    data = json.load(f)

ws_frames = data.get('websocket_frames', [])
received = [f for f in ws_frames if f.get('direction') == 'received']

# Parse Socket.IO frames (format: 3:::{"data":{...},"ID":...})
betting_events = []
for frame in received:
    raw = frame.get('data', '')
    if raw.startswith('3:::'):
        try:
            payload = raw[4:]  # Remove '3:::'
            parsed = json.loads(payload)
            inner_data = parsed.get('data', {})
            
            # Look for sports/betting related keys
            inner_str = str(inner_data).lower()
            if 'sport' in inner_str or 'odd' in inner_str or 'event' in inner_str or 'match' in inner_str or 'game' in inner_str:
                betting_events.append(inner_data)
                print(f'Found betting frame with keys: {list(inner_data.keys())}')
                
                # Check for specific betting structures
                for key in ['sports', 'events', 'fixtures', 'matches', 'odds', 'games', 'competitions']:
                    if key in inner_data:
                        val = inner_data[key]
                        print(f' -> {key}: {type(val).__name__}, len={len(str(val))}')
                        if isinstance(val, (list, dict)) and len(val) > 0:
                            print(f'    Sample: {str(val)[:200]}')
        except Exception as e:
            pass

print(f'\nTotal betting-related frames: {len(betting_events)}')
