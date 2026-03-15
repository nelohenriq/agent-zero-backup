#!/usr/bin/env python3
"""
Placard Sports Betting API Scraper
Extracts soccer and basketball events with markets and odds
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
PREFETCH_FILE = '/a0/usr/projects/scraping_betting_sites/placard_prefetch_response.json'
SOCCER_OUTPUT = '/a0/usr/projects/scraping_betting_sites/placard_soccer.json'
BASKETBALL_OUTPUT = '/a0/usr/projects/scraping_betting_sites/placard_basketball.json'

# Sport IDs
SPORT_SOCCER = 5
SPORT_BASKETBALL = 4942


def load_prefetch_data(filepath: str) -> Optional[Dict]:
    """Load and parse JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON from {filepath}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return None


def validate_data_structure(data: Dict) -> bool:
    """Validate the expected data structure"""
    required_fields = ['data']
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return False

    if 'data' not in data or 'model' not in data['data']:
        logger.error("Invalid data structure: missing data.model")
        return False

    model = data['data']['model']

    required_model_fields = ['events', 'markets']
    for field in required_model_fields:
        if field not in model:
            logger.error(f"Missing model field: {field}")
            return False

    return True


def extract_match_data(event: Dict) -> Dict:
    """Extract match information from event"""
    match_data = {
        'eventId': event.get('id'),
        'sportId': event.get('sportId'),
        'matchName': event.get('name'),
        'startTime': event.get('kickoffTime') or event.get('startDate'),
        'competition': event.get('competition') or event.get('league'),
        'marketRefs': event.get('marketRefs', []),
        'markets': []
    }

    # Extract participants
    event_participants = event.get('eventParticipants', event.get('participants', []))
    match_data['participants'] = []
    for participant in event_participants:
        match_data['participants'].append({
            'name': participant.get('name'),
            'type': participant.get('type')  # HOME, AWAY, etc.
        })

    return match_data


def extract_selection(selection: Dict) -> Dict:
    """Extract selection data with odds"""
    return {
        'id': selection.get('id'),
        'name': selection.get('name'),
        'price': selection.get('price'),
        'decimalOdds': selection.get('decimalOdds'),
        'selectionType': selection.get('selectionType')
    }


def extract_competition(market: Dict, all_competitions: List[Dict]) -> str:
    """Extract competition name from market or competitions list"""
    comp_id = market.get('competitionRef')
    if comp_id and all_competitions:
        for comp in all_competitions:
            if comp.get('id') == comp_id:
                return comp.get('name', 'Unknown')
    return market.get('competitionRefName') or market.get('competitionName', 'Unknown')


def find_markets_for_event(event_id: str, all_markets: List[Dict], 
                           all_selections: List[Dict],
                           all_competitions: List[Dict]) -> List[Dict]:
    """Find markets associated with an event"""
    event_markets = []

    for market in all_markets:
        # Check if market belongs to this event
        market_event_id = market.get('eventRef')
        if str(market_event_id) == str(event_id):
            market_data = {
                'marketId': market.get('id'),
                'marketName': market.get('name'),
                'marketType': market.get('marketType'),
                'competition': extract_competition(market, all_competitions),
                'isHandicap': market.get('isHandicap', False),
                'selections': []
            }

            # Get selections for this market
            selection_refs = market.get('selectionRefs', [])

            if isinstance(selection_refs, list) and all_selections:
                for sel_id in selection_refs:
                    for selection in all_selections:
                        if selection.get('id') == sel_id:
                            selection_data = extract_selection(selection)
                            market_data['selections'].append(selection_data)
                            break

            event_markets.append(market_data)

    return event_markets


def filter_events_by_sport(events: List[Dict], sport_id: int) -> List[Dict]:
    """Filter events by sport ID"""
    filtered = []
    for event in events:
        if event.get('sportId') == sport_id:
            filtered.append(event)
    return filtered


def process_events(data: Dict, sport_id: int, sport_name: str) -> Dict:
    """Process events for a specific sport"""
    model = data['data']['model']
    events = model.get('events', [])
    markets = model.get('markets', [])
    selections = model.get('selections', [])
    competitions = model.get('competitions', [])

    # Filter events by sport
    sport_events = filter_events_by_sport(events, sport_id)
    logger.info(f"Found {len(sport_events)} {sport_name} events (sportId: {sport_id})")

    processed_matches = []
    total_markets = 0

    for event in sport_events:
        match_data = extract_match_data(event)

        # Find markets for this event
        event_markets = find_markets_for_event(
            event.get('id'), markets, selections, competitions
        )

        match_data['markets'] = event_markets
        match_data['marketCount'] = len(event_markets)

        processed_matches.append(match_data)
        total_markets += len(event_markets)

    return {
        'sportId': sport_id,
        'sportName': sport_name,
        'extractionTime': datetime.now().isoformat(),
        'totalEvents': len(processed_matches),
        'totalMarkets': total_markets,
        'matches': processed_matches
    }


def save_json(data: Dict, filepath: str) -> bool:
    """Save data to JSON file with indentation"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        file_size = len(json.dumps(data))
        logger.info(f"Saved to {filepath} ({file_size} bytes)")
        return True
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")
        return False


def main() -> bool:
    """Main execution function"""
    logger.info("=" * 50)
    logger.info("Placard Sports API Scraper")
    logger.info("=" * 50)

    # Load data
    data = load_prefetch_data(PREFETCH_FILE)
    if not data:
        logger.error("Failed to load prefetch data")
        return False

    # Validate structure
    if not validate_data_structure(data):
        logger.error("Data validation failed")
        return False

    logger.info("Data structure validated successfully")

    # Process soccer (sportId: 5)
    logger.info("-" * 50)
    logger.info("Processing Soccer events...")
    soccer_data = process_events(data, SPORT_SOCCER, "Soccer")

    # Process basketball (sportId: 4942)
    logger.info("-" * 50)
    logger.info("Processing Basketball events...")
    basketball_data = process_events(data, SPORT_BASKETBALL, "Basketball")

    # Save outputs
    logger.info("-" * 50)
    logger.info("Saving output files...")

    soccer_saved = save_json(soccer_data, SOCCER_OUTPUT)
    basketball_saved = save_json(basketball_data, BASKETBALL_OUTPUT)

    success = True
    if not soccer_saved or not basketball_saved:
        success = False

    # Final summary
    logger.info("\n" + "=" * 50)
    logger.info("EXTRACTION COMPLETE")
    logger.info("=" * 50)
    logger.info(f"Soccer: {soccer_data['totalEvents']} events, {soccer_data['totalMarkets']} markets")
    logger.info(f"Basketball: {basketball_data['totalEvents']} events, {basketball_data['totalMarkets']} markets")
    logger.info(f"Output files: {SOCCER_OUTPUT}, {BASKETBALL_OUTPUT}")

    return success


if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        exit(130)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        exit(1)
