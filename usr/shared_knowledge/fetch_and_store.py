"""Query the local SearXNG instance, store each result as markdown,
update the import manifest and rebuild the FAISS index.
Usage: python fetch_and_store.py "your query here"
"""
import sys, os, json, hashlib, requests, datetime, subprocess

# Configuration – adjust if your SearXNG runs on a different host/port
SEARXNG_URL = 'http://127.0.0.1:55510/search'
WEB_DIR = '/a0/usr/shared_knowledge/web'
MEM_DIR = '/a0/usr/shared_knowledge/.a0proj/memory'
IMPORT_JSON = os.path.join(MEM_DIR, 'knowledge_import.json')

if len(sys.argv) < 2:
    print('Error: query string required')
    sys.exit(1)
query = ' '.join(sys.argv[1:])

# -------------------------------------------------------------------
# 2️⃣ Perform the SearXNG request
# -------------------------------------------------------------------
params = {'q': query, 'format': 'json'}
try:
    resp = requests.get(SEARXNG_URL, params=params, timeout=30)
except Exception as e:
    print('SearXNG request failed:', e)
    sys.exit(1)

if resp.status_code != 200:
    print('SearXNG request failed:', resp.status_code, resp.text)
    sys.exit(1)

results = resp.json().get('results', [])
if not results:
    print('No results returned for the query.')
    sys.exit(0)

# -------------------------------------------------------------------
# 3️⃣ Store each result as a markdown file and collect manifest entries
# -------------------------------------------------------------------
import_path = []
for r in results:
    title = r.get('title') or 'untitled'
    url = r.get('url') or ''
    snippet = r.get('content') or ''
    fetched = datetime.datetime.utcnow().isoformat() + 'Z'
    # Build a safe filename – truncate to 60 chars for readability
    safe_name = ''.join(c if c.isalnum() else '_' for c in title)[:60]
    md_path = os.path.join(WEB_DIR, f"{safe_name}.md")
    with open(md_path, 'w') as f:
        f.write(f"# {title}\n\n")
        f.write(f"*Source*: {url}\n")
        f.write(f"*Fetched*: {fetched}\n\n")
        f.write(snippet)
    checksum = hashlib.sha256(open(md_path, 'rb').read()).hexdigest()
    import_path.append({
        'id': checksum[:12],
        'file_path': md_path,
        'checksum': checksum,
    })
    print(f'Stored: {md_path}')

# -------------------------------------------------------------------
# 4️⃣ Load existing manifest safely – it may be a dict, a list, or empty
# -------------------------------------------------------------------
if os.path.exists(IMPORT_JSON):
    try:
        with open(IMPORT_JSON, 'r') as f:
            existing = json.load(f)
    except Exception as e:
        print('Failed to parse existing manifest, starting fresh:', e)
        existing = []
else:
    existing = []

# Normalise to a list
if isinstance(existing, dict):
    # If it was accidentally stored as a dict, keep its values (if any)
    existing = list(existing.values())
elif not isinstance(existing, list):
    # Any other unexpected type – reset to empty list
    existing = []

# Append new entries and write back
existing.extend(import_path)
with open(IMPORT_JSON, 'w') as f:
    json.dump(existing, f, indent=2)
print(f'Updated manifest with {len(import_path)} new entries (total now {len(existing)})')

# -------------------------------------------------------------------
# 5️⃣ Re‑index FAISS using the offline script present in shared_knowledge
# -------------------------------------------------------------------
idx_script = '/a0/usr/shared_knowledge/reindex_faiss_offline.py'
if os.path.exists(idx_script):
    try:
        subprocess.run(['python', idx_script], check=True)
        print('FAISS re‑index completed successfully.')
    except subprocess.CalledProcessError as e:
        print('FAISS re‑index script failed:', e)
else:
    print('FAISS re‑index script not found; you may run it manually.')
