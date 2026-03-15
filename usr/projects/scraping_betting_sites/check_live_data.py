import json

# Check the live captured data file
with open('processed_sports/solverde_live_captured_data.json') as f:
 data = json.load(f)

print(f"=== solverde_live_captured_data.json ===")
print(f"Type: {type(data)}, Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")

for i, item in enumerate(data):
 print(f"\n--- Item {i+1} ---")
 if isinstance(item, dict):
 for k, v in item.items():
 if isinstance(v, str):
 print(f"{k}: {v[:150]}...")
 elif isinstance(v, (list, dict)):
 print(f"{k}: {type(v).__name__} with {len(v) if hasattr(v, '__len__') else 'N/A'} items")
 else:
 print(f"{k}: {v}")
 elif isinstance(item, str):
 print(item[:200])

# Now check HTML for embedded JSON
print("\n\n=== Looking for embedded JSON in HTML ===")
with open('processed_sports/solverde_final_capture.json') as f:
 capture = json.load(f)

html = capture.get('html_source', '')
# Find script tags with data
import re
# Look for JSON data in script tags
script_matches = re.findall(r'<script[^>]*>([^<]+)</script>', html, re.I)
print(f"Found {len(script_matches)} script tag contents")

# Look for window.__DATA or similar patterns
data_patterns = re.findall(r'window\.(\w+)\s*=\s*(\{.+?\});', html, re.DOTALL)
print(f"Found {len(data_patterns)} window.*= patterns")

# Look for __NEXT_DATA__ or similar (Next.js)
next_data = re.findall(r'__NEXT_DATA__[^>]*>([^<]+)</script>', html, re.I)
print(f"Found {len(next_data)} __NEXT_DATA__ patterns")
