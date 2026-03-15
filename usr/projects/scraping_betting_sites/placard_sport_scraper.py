#!/usr/bin/env python3
"""
Placard Sports Betting API Scraper
Extracts soccer and basketball match data with markets and odds.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Define paths based on active project
PROJECT_DIR = Path('/a0/usr/projects/scraping_betting_sites')
PREFETCH_FILE = PROJECT_DIR / 'placard_prefetch_response.json'
SOCCER_OUTPUT = PROJECT_DIR / 'placard_soccer.json'
BASKETBALL_OUTPUT = PROJECT_DIR / 'placard_basketball.json'

# Sport names to filter (from the data: sportId is string, not integer)
SPORT_SOCCER = 'soccer'
SPORT_BASKETBALL = 'basketball'


def load_prefetch_data():
    """Load prefetch data from saved file."""
    try:
        print(f"Loading prefetch data from {PREFETCH_FILE}...")
        with open(PREFETCH_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required keys
        if 'events' not in data:
            raise KeyError("'events' key not found in prefetch data")
        if 'sportsMetaInformation' not in data:
            raise KeyError("'sportsMetaInformation' key not found in prefetch data")
        if 'markets' not in data:
            raise KeyError("'markets' key not found in prefetch data")
        
        print(f"Loaded {len(data.get('events', []))} events")
        print(f"Loaded {len(data.get('sportsMetaInformation', {}))} sports meta entries")
        print(f"Loaded {len(data.get('markets', {}))} markets")
        return data
        
    except FileNotFoundError:
        print(f"ERROR: Prefetch file not found: {PREFETCH_FILE}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in prefetch file: {e}")
        return None
    except KeyError as e:
        print(f"ERROR: Missing required key in data structure: {e}")
        return None


def filter_events_by_sport(events_data, sport_id):
    """Filter events for a specific sport ID."""
    filtered = [event for event in events_data if event.get('sportId') == sport_id]
    print(f"Found {len(filtered)} events for sport '{sport_id}'")
    return filtered


def extract_market_details(market_ids, markets_pool):
    """Extract market details by IDs."""
    market_details = []
    for market_id in market_ids:
        market_data = markets_pool.get(str(market_id))
        if market_data:
            market_info = {
                'marketId': market_id,
                'marketName': market_data.get('name', 'Unknown'),
                'marketType': market_data.get('type', 'Unknown'),
                'marketLine': market_data.get('marketLine', []),
                'odds': []
            }
            
            # Extract odds from market lines
            for line in market_data.get('marketLine', []):
                odds_item = {
                    'selectionId': line.get('id'),
                    'name': line.get('name'),
                    'odds': line.get('odds'),
                    'handicap': line.get('handicap'),
                    'isActive': line.get('valid', True)
                }
                market_info['odds'].append(odds_item)
            
            market_details.append(market_info)
    
    return market_details


def extract_participants(event_data):
    """Extract participant/team information from event data."""
    participants = []
    home_team = event_data.get('homeTeamName', '')
    away_team = event_data.get('awayTeamName', '')
    
    if home_team:
        participants.append({
            'type': 'home',
            'name': home_team
        })
    if away_team:
        participants.append({
            'type': 'away',
            'name': away_team
        })
    
    return participants


def extract_event_data(event, sports_meta, markets_pool):
    """Extract complete event data with markets and odds."""
    event_data = {
        'eventId': event.get('eventId'),
        'name': event.get('name', 'Unknown'),
        'sportId': event.get('sportId'),
        'competitionId': event.get('competitionId'),
        'competitionName': event.get('competitionName', ''),
        'startTime': event.get('startTime'),
        'regionId': event.get('regionId'),
        'regionName': event.get('regionName', ''),
        'valid': event.get('valid', False),
        'live': event.get('live', False),
        'participants': extract_participants(event),
        'markets': []
    }
    
    # Get market IDs from event
    market_ids = event.get('markets', [])
    
    # Extract market details
    if market_ids and markets_pool:
        event_data['markets'] = extract_market_details(market_ids, markets_pool)
    
    # Add sport name from meta
    sport_meta = sports_meta.get(event.get('sportId', ''), {})
    event_data['sportName'] = sport_meta.get('name', event.get('sportId', 'Unknown'))
    
    return event_data


def save_results(data, output_path):
    """Save results to JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Results saved to: {output_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to save results to {output_path}: {e}")
        return False


def main():
    """Main execution function."""
    print("=" * 60)
    print("PLACARD SPORTS BETTING API SCRAPER")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Load prefetch data
    data = load_prefetch_data()
    if not data:
        return False
    
    events = data['events']
    sports_meta = data['sportsMetaInformation']
    markets_pool = data['markets']
    
    # Filter events by sport
    print("\n" + "-" * 40)
    print("FILTERING EVENTS BY SPORT")
    print("-" * 40)
    
    soccer_events = filter_events_by_sport(events, SPORT_SOCCER)
    basketball_events = filter_events_by_sport(events, SPORT_BASKETBALL)
    
    # Extract detailed data for each sport
    print("\n" + "-" * 40)
    print("EXTRACTING EVENT DETAILS")
    print("-" * 40)
    
    soccer_output = {
        'sport': SPORT_SOCCER,
        'extractionTimestamp': datetime.now().isoformat(),
        'totalEvents': len(soccer_events),
        'events': []
    }
    
    basketball_output = {
        'sport': SPORT_BASKETBALL,
        'extractionTimestamp': datetime.now().isoformat(),
        'totalEvents': len(basketball_events),
        'events': []
    }
    
    # Process soccer events
    print(f"\nProcessing {len(soccer_events)} soccer events...")
    for idx, event in enumerate(soccer_events, 1):
        event_data = extract_event_data(event, sports_meta, markets_pool)
        soccer_output['events'].append(event_data)
        if idx % 5 == 0 or idx == len(soccer_events):
            print(f"  Processed {idx}/{len(soccer_events)} soccer events")
    
    # Process basketball events
    print(f"\nProcessing {len(basketball_events)} basketball events...")
    for idx, event in enumerate(basketball_events, 1):
        event_data = extract_event_data(event, sports_meta, markets_pool)
        basketball_output['events'].append(event_data)
        if idx % 5 == 0 or idx == len(basketball_events):
            print(f"  Processed {idx}/{len(basketball_events)} basketball events")
    
    # Calculate statistics
    total_markets_soccer = sum(len(evt['markets']) for evt in soccer_output['events'])
    total_odds_soccer = sum(
        len(market.get('odds', [])) 
        for evt in soccer_output['events'] 
        for market in evt['markets']
    )
    
    total_markets_basketball = sum(len(evt['markets']) for evt in basketball_output['events'])
    total_odds_basketball = sum(
        len(market.get('odds', [])) 
        for evt in basketball_output['events'] 
        for market in evt['markets']
    )
    
    soccer_output['totalMarkets'] = total_markets_soccer
    soccer_output['totalOdds'] = total_odds_soccer
    
    basketball_output['totalMarkets'] = total_markets_basketball
    basketball_output['totalOdds'] = total_odds_basketball
    
    # Save results
    print("\n" + "-" * 40)
    print("SAVING RESULTS")
    print("-" * 40)
    
    save_results(soccer_output, SOCCER_OUTPUT)
    save_results(basketball_output, BASKETBALL_OUTPUT)
    
    # Print summary
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"\nSoccer:")
    print(f"  - Events: {soccer_output['totalEvents']}")
    print(f"  - Markets: {soccer_output['totalMarkets']}")
    print(f"  - Total odds: {soccer_output['totalOdds']}")
    print(f"  - Output: {SOCCER_OUTPUT}")
    print(f"\nBasketball:")
    print(f"  - Events: {basketball_output['totalEvents']}")
    print(f"  - Markets: {basketball_output['totalMarkets']}")
    print(f"  - Total odds: {basketball_output['totalOdds']}")
    print(f"  - Output: {BASKETBALL_OUTPUT}")
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
