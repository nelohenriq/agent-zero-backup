import json

with open('processed_sports/solverde_extended_60s_20260307_174905.json') as f:
 data = json.load(f)

api_responses = data.get('api_responses', [])
print(f"Total API responses: {len(api_responses)}\n")

# Look at each response
for i, resp in enumerate(api_responses):
 url = resp.get('url', '')
 status = resp.get('status', 0)
 body = resp.get('body', '')
 
 print(f"\n--- Response {i+1} ---")
 print(f"URL: {url}")
 print(f"Status: {status}")
 print(f"Body length: {len(body)}")
 
 if status == 200 and body and len(body) > 100:
 # Check if it's JSON
 if body.strip().startswith('{') or body.strip().startswith('['):
 try:
 json_body = json.loads(body)
 print(f"JSON keys: {list(json_body.keys())[:10]}")
 
 # Look for sports data
 if 'sports' in str(json_body).lower() or 'futebol' in str(json_body).lower() or 'odds' in str(json_body).lower():
 print("=== POTENTIAL SPORTS DATA FOUND ===")
 print(json.dumps(json_body, indent=2, ensure_ascii=False)[:3000])
 except:
 print(f"Body preview: {body[:500]}")
 else:
 print(f"Body preview: {body[:500]}")

