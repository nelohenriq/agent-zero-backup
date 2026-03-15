import os, json, hashlib, subprocess, sys

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

base = '/a0/usr/shared_knowledge'
web_dir = os.path.join(base, 'web')
mem_dir = os.path.join(base, '.a0proj', 'memory')
import_path = os.path.join(mem_dir, 'knowledge_import.json')

entries = []
for fn in sorted(os.listdir(web_dir)):
    if not fn.lower().endswith('.md'):
        continue
    fp = os.path.join(web_dir, fn)
    checksum = sha256_file(fp)
    entries.append({
        'id': checksum[:12],
        'file_path': fp,
        'checksum': checksum,
    })

# write manifest
with open(import_path, 'w') as f:
    json.dump(entries, f, indent=2)
print(f'Wrote {len(entries)} entries to {import_path}')

# Re‑index FAISS (requires the existing embedder script – we assume a helper exists)
# For simplicity we call the project's existing index script if present
index_script = '/a0/usr/projects/second_brain/.a0proj/memory/reindex_faiss.py'
if os.path.exists(index_script):
    subprocess.run(['python', index_script, '--source-dir', web_dir, '--output-dir', mem_dir], check=True)
    print('FAISS re‑index completed using existing script')
else:
    print('FAISS re‑index script not found – you will need to run your own indexing command.')
