
import json
import glob

files_to_check = [
 'processed_sports/solverde_extended_60s_20260307_174905.json',
 'processed_sports/solverde_api_capture_full_20260307_001048.json',
 'processed_sports/extracted_betting_data.json',
 'processed_sports/solverde_live_captured_data.json'
]

for fpath in files_to_check:
    try:
        with open(fpath, 'r', errors='ignore') as f:
            data = json.load(f)
        print(f'=== {fpath} ===')
        print(f'Type: {type(data)}, Keys: {list(data.keys())[:10] if isinstance(data, dict) else "N/A"}')
        
        if 'api_responses' in data:
            print(f'API responses: {len(data["api_responses"])}')
            for resp in data['api_responses']:
                url = resp.get('url', '')
                if 'sport' in url.lower() and resp.get('status') == 200:
                    body = resp.get('body', '')
                    if body and len(body) > 200:
                        print(f'\n*** Sports API: {url}')
                        print(body[:2500])
                        break
    except Exception as e:
        print(f'Error {fpath}: {e}')
