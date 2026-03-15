import json

with open('processed_sports/solverde_final_capture.json') as f:
 data = json.load(f)

print("=== HTML Source ===")
html = data.get('html_source', '')
print(f"Length: {len(html)} chars")
# Look for betting-related patterns in HTML
import re
patterns = ['odds', 'betting', 'aposta', 'futebol', 'liga', 'jogo', 'Resultado', 'over', 'under', 'handicap']
for p in patterns:
 matches = len(re.findall(p, html, re.I))
 if matches > 0:
  print(f" '{p}': {matches} occurrences")

print("\n=== Network Responses ===")
for i, resp in enumerate(data.get('network_responses', [])[:5]):
 print(f"\n--- Response {i+1} ---")
 if isinstance(resp, dict):
  print(f"URL: {resp.get('url', 'N/A')[:100]}")
  print(f"Status: {resp.get('status')}")
  body = resp.get('response', {}).get('body', {})
  if isinstance(body, dict):
   keys = list(body.keys())[:10]
   print(f"Body keys: {keys}")
   # Check for sports data
   if 'sports' in str(body).lower() or 'matches' in str(body).lower():
    print(" ** Contains sports/matches data!")
  elif isinstance(body, str) and len(body) > 100:
   print(f"Body preview: {body[:200]}...")
