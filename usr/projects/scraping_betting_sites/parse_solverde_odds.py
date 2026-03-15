import json
import os
from pathlib import Path

input_file = Path('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_api_intercept_fixed_20260307_004801.json')
output_file = Path('/a0/usr/projects/scraping_betting_sites/solverde_with_odds.json')

matches = []

if input_file.exists():
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            responses = json.load(f)
        
        print(f'Processing {len(responses)} network responses...')
        
        for i, resp in enumerate(responses):
            # Get body content
            body = resp.get('body', '') or resp.get('body_preview', '')
            if not body:
                continue
            
            # Ensure body is a string
            if isinstance(body, dict) or isinstance(body, list):
                data = body
            else:
                try:
                    data = json.loads(str(body))
                except json.JSONDecodeError:
                    continue
            
            # Recursive search function
            def extract_matches(obj, path=''):
                found = []
                if isinstance(obj, dict):
                    # Check for match-like structure
                    # Heuristic: has 'id' and either 'name' or team indicators
                    is_match = False
                    if 'id' in obj:
                        if 'name' in obj or 'homeTeam' in obj or 'awayTeam' in obj or 'home' in obj or 'away' in obj:
                            is_match = True
                    
                    if is_match:
                        match_data = {
                            'match_id': obj.get('id'),
                            'name': obj.get('name', ''),
                            'home_team': obj.get('homeTeam') or obj.get('home') or obj.get('name', '').split(' - ')[0] if ' - ' in str(obj.get('name', '')) else None,
                            'away_team': obj.get('awayTeam') or obj.get('away') or obj.get('name', '').split(' - ')[1] if ' - ' in str(obj.get('name', '')) else None,
                            'start_time': obj.get('startTime') or obj.get('start_time') or obj.get('date'),
                            'sport_id': obj.get('sportId') or obj.get('sport_id'),
                            'markets': obj.get('marketLines') or obj.get('markets') or obj.get('odds') or obj.get('selections'),
                            'source_path': path
                        }
                        # Clean up names if split from 'name'
                        if not match_data['home_team'] and match_data['name'] and ' - ' in match_data['name']:
                            parts = match_data['name'].split(' - ', 1)
                            match_data['home_team'] = parts[0].strip()
                            match_data['away_team'] = parts[1].strip()
                        found.append(match_data)
                    
                    # Recurse
                    for k, v in obj.items():
                        found.extend(extract_matches(v, f'{path}.{k}'))
                elif isinstance(obj, list):
                    for idx, item in enumerate(obj):
                        found.extend(extract_matches(item, f'{path}[{idx}]'))
                return found
            
            extracted = extract_matches(data)
            matches.extend(extracted)
        
        print(f'\nTotal matches found: {len(matches)}')
        
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        
        print(f'Saved to {output_file}')
        if matches:
            print('\nSample match with odds:')
            s = matches[0]
            print(f"Match: {s['name']}")
            print(f"Home: {s['home_team']}, Away: {s['away_team']}")
            if s['markets']:
                print(f"Markets type: {type(s['markets'])}")
                if isinstance(s['markets'], dict):
                    print(f"Market keys: {list(s['markets'].keys())[:5]}...")
                else:
                    print(f"Markets preview: {str(s['markets'])[:200]}...")
            else:
                print("No markets found in this sample.")
                
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
else:
    print('Input file not found')
