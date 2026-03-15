import json
import re

# Load the WebSocket frames
with open('/a0/usr/projects/scraping_betting_sites/processed_sports/solverde_ws_v8_20260307_164139.json') as f:
 data = json.load(f)

recv = data.get('frames_received', [])

# Frame 5 contains sports list - extract directly from preview text
# Looking at raw text: there's a MESSAGE header then JSON
# Let's just find all JSON objects in all received frames

all_sports = []
all_matches = []
all_selections = []

for i, frame in enumerate(recv):
 txt = frame.get('text', '')
 
 # Find JSON blocks - look for {...} patterns
 json_matches = re.findall(r'\{[^{}]*\}', txt)
 for jm in json_matches:
 try:
 obj = json.loads(jm)
 # Check for sports-related keys
 if 'id' in obj:
  if obj.get('id') == 'soccer' or obj.get('canonicalName') == 'Football':
   all_sports.append(obj)
 if 'items' in obj and isinstance(obj['items'], list):
  for item in obj['items']:
   if isinstance(item, dict):
    if item.get('id') == 'soccer':
     all_sports.append(item)
    if 'name' in item and 'futebol' in str(item.get('name','')).lower():
     all_matches.append(item)
 if 'selections' in obj:
  all_selections.extend(obj['selections'])
 except:
 pass

# More direct approach - look for specific text patterns in frames
print("=== SCANNING ALL FRAMES FOR KEY DATA ===\n")

# Sports list
for i, frame in enumerate(recv):
 txt = frame.get('text', '')
 if '"id":"soccer"' in txt or '"name":"Futebol"' in txt:
  print(f"Frame {i}: Contains soccer/Futebol!")
  # Extract the actual JSON
  start = txt.find('{"id')
  if start > 0:
   try:
    # Find matching brace
    depth = 0
    end = start
    for j, c in enumerate(txt[start:], start):
     if c == '{': depth += 1
     elif c == '}': depth -= 1
     if depth == 0:
      end = j + 1
      break
    json_str = txt[start:end]
    sports_data = json.loads(json_str)
    print(f"Keys: {list(sports_data.keys())}")
    if 'items' in sports_data:
     print(f"Sports items: {json.dumps(sports_data['items'], ensure_ascii=False)[:500]}")
   except Exception as e:
    print(f"Parse error: {e}")

# Look for matches/events
print("\n=== LOOKING FOR MATCH/EVENT DATA ===")
for i, frame in enumerate(recv):
 txt = frame.get('text', '')
 if '"type":"MRES"' in txt or 'Full Time Result' in txt:
  print(f"\nFrame {i}: Contains betting odds!")
  # Try to extract JSON with selections
  if 'selections' in txt:
   sel_match = re.search(r'"selections":\[[^\]]+\]', txt)
   if sel_match:
    print(f"Selections: {sel_match.group()[:300]}")

