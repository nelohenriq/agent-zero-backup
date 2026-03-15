import os, json, pickle
from pathlib import Path
import numpy as np, faiss
from sentence_transformers import SentenceTransformer

WEB_DIR = '/a0/usr/shared_knowledge/web'
MEM_DIR = '/a0/usr/shared_knowledge/.a0proj/memory'
MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

print('🔎 Scanning markdown files…')
paths = sorted(Path(WEB_DIR).glob('*.md'))
if not paths:
    print('⚠️ No markdown files found – abort')
    raise SystemExit(1)

model = SentenceTransformer(MODEL)
vectors = []
metadata = []
for p in paths:
    txt = p.read_text(errors='ignore')
    vec = model.encode(txt)
    vectors.append(vec)
    metadata.append({
        'id': p.stem,
        'title': p.stem.replace('_', ' '),
        'path': str(p)
    })

vectors_np = np.array(vectors).astype('float32')
idx = faiss.IndexFlatL2(vectors_np.shape[1])
idx.add(vectors_np)

os.makedirs(MEM_DIR, exist_ok=True)
faiss.write_index(idx, os.path.join(MEM_DIR, 'index.faiss'))
with open(os.path.join(MEM_DIR, 'index.pkl'), 'wb') as f:
    pickle.dump(metadata, f)
print(f'✅ Indexed {len(vectors)} documents → {os.path.join(MEM_DIR, "index.faiss")}')
