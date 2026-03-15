#!/usr/bin/env python3
"""Offline FAISS re‑indexer for the shared knowledge base.
   * Reads every *.md file under /a0/usr/shared_knowledge/web/.
   * Creates a deterministic pseudo‑embedding (SHA‑256 → float32 vector).
   * Builds a FlatL2 FAISS index and stores it at
     /a0/usr/shared_knowledge/.a0proj/memory/index.faiss.
   * Writes a metadata list (id, title, file_path) to
     index_metadata.json for later lookup.
"""
import os, json, hashlib
from pathlib import Path
import numpy as np, faiss

WEB_DIR = '/a0/usr/shared_knowledge/web'
MEM_DIR = '/a0/usr/shared_knowledge/.a0proj/memory'
INDEX_PATH = os.path.join(MEM_DIR, 'index.faiss')
METADATA_PATH = os.path.join(MEM_DIR, 'index_metadata.json')
DIM = 128  # length of the deterministic pseudo‑embedding

def pseudo_embed(text: str, dim: int = DIM) -> np.ndarray:
    """Return a deterministic float32 vector of length *dim*.
       We hash the full text, repeat the digest to fill the required byte count,
       and view it as little‑endian float32 numbers.
    """
    digest = hashlib.sha256(text.encode('utf-8')).digest()
    # repeat digest to reach dim*4 bytes (float32 = 4 bytes)
    repeats = (dim * 4 + len(digest) - 1) // len(digest)
    raw = (digest * repeats)[: dim * 4]
    return np.frombuffer(raw, dtype=np.float32)

# Gather all markdown files
md_paths = sorted(Path(WEB_DIR).rglob('*.md'))
if not md_paths:
    print('⚠️ No markdown files found – nothing to index.')
    raise SystemExit(0)

vectors = []
metadata = []
for p in md_paths:
    txt = p.read_text(errors='ignore')
    vec = pseudo_embed(txt)
    vectors.append(vec)
    metadata.append({
        'id': hashlib.sha256(txt.encode()).hexdigest()[:12],
        'title': p.stem.replace('_', ' '),
        'file_path': str(p)
    })

# Build FAISS index
xb = np.vstack(vectors).astype('float32')
index = faiss.IndexFlatL2(DIM)
index.add(xb)
os.makedirs(MEM_DIR, exist_ok=True)
faiss.write_index(index, INDEX_PATH)
with open(METADATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)
print(f'✅ Indexed {len(vectors)} documents → {INDEX_PATH}')
