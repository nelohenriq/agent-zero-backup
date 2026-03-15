import json

with open('processed_sports/solverde_ws_live_20260307_161713.json') as f:
 data = json.load(f)

ws_frames = data.get('websocket_frames', [])

print("=== EXTRACTING BETTING ODDS FROM WEBSOCKET ===\n")

# Find frames with market/odds data
for frame in ws_frames:
 if frame.get('direction') == 'received':
  payload = frame.get('data', '')
  # Look for market data (Resultado, odds, selections)
  if 'selections' in payload and ('odds' in payload.lower() or 'MRES' in payload or 'HCTG' in payload):
   try:
    # Extract JSON from the message
    if '{"id"' in payload:
     start = payload.find('{"id"')
     market_json = json.loads(payload[start:])
     
     print(f"Market: {market_json.get('name', 'N/A')} ({market_json.get('canonicalName', 'N/A')})")
     print(f"Type: {market_json.get('type', 'N/A')}")
     
     selections = market_json.get('selections', [])
     for sel in selections:
      outcome = sel.get('outcome', 'N/A')
      odds_val = sel.get('odds', 'N/A')
      status = sel.get('status', 'N/A')
      print(f"  -> {outcome}: {odds_val} (status: {status})")
     print()
   except Exception as e:
    pass
