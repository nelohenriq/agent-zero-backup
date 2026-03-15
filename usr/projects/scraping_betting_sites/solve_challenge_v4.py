import json
import requests
import re
import os

# Load the challenge response
if not os.path.exists('placard_debug_responses.json'):
    print("Error: placard_debug_responses.json not found.")
    exit(1)

with open('placard_debug_responses.json', 'r') as f:
    responses = json.load(f)

challenge_data = responses[0]['data']
tc = challenge_data.get('tc')
ra = challenge_data.get('ra', {})
req_id = ra.get('req')

print(f"Challenge Token (tc): {tc[:20]}...")
print(f"Request ID (req): {req_id}")

# Extract tr_uuid from the HTML file if possible
tr_uuid = "20260307-1028-09ca-b6fe-af091c0fc2d8" # Default fallback
if os.path.exists('placard_raw_body.html'):
    with open('placard_raw_body.html', 'r') as f:
        html_content = f.read()
    match = re.search(r'tr_uuid=([\w-]+)', html_content)
    if match:
        tr_uuid = match.group(1)
        print(f"Found tr_uuid in HTML: {tr_uuid}")
    else:
        print(f"tr_uuid not found in HTML, using default: {tr_uuid}")
else:
    print(f"placard_raw_body.html not found, using default tr_uuid: {tr_uuid}")

# Construct the URL
base_url = "https://api.placard.bet/prefetch"
# Based on the JS: redirect_link + suffix, where suffix is 'fp=-7'
# And the original URL had tr_uuid
final_url = f"{base_url}?tr_uuid={tr_uuid}&fp=-7&tc={tc}"
print(f"Attempting to fetch: {final_url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://placard.bet/",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Cookie": f"tc={tc}"
}

try:
    response = requests.get(final_url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if 'eventGroups' in data:
                print("SUCCESS: Received valid sports data!")
                output_file = 'placard_challenge_solved_data_v4.json'
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Saved to {output_file}")
            else:
                print("Response is JSON but missing 'eventGroups'.")
                print(f"Keys: {list(data.keys())}")
                # Save anyway for inspection
                with open('placard_challenge_solved_data_v4_partial.json', 'w') as f:
                    json.dump(data, f, indent=2)
        except json.JSONDecodeError:
            print("Response is not valid JSON.")
            print(f"Content preview: {response.text[:500]}")
    else:
        print(f"Failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error during request: {e}")
    import traceback
    traceback.print_exc()
