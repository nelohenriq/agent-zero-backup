#!/usr/bin/env python3
"""Generate a D3‑compatible graph JSON from the FAISS metadata.
   Nodes: each markdown document (title & path).
   Edges: simple co‑occurrence based on shared keywords extracted from titles.
   The output is written to `/a0/usr/shared_knowledge/graph.json`.
"""
import json, re, os
from pathlib import Path

MEM_DIR = '/a0/usr/shared_knowledge/.a0proj/memory'
META_PATH = os.path.join(MEM_DIR, 'index_metadata.json')
OUT_PATH = '/a0/usr/shared_knowledge/graph.json'

# Load metadata (list of dicts with id, title, file_path)
with open(META_PATH, 'r', encoding='utf-8') as f:
    meta = json.load(f)

# Helper to extract simple keywords from titles (lowercase words >2 chars)
def keywords(title):
    words = re.findall(r"[a-zA-Z]{3,}", title.lower())
    return set(words)

nodes = []
edges = []
title_to_id = {}
for entry in meta:
    nid = entry['id']
    title = entry['title']
    path = entry['file_path']
    nodes.append({"id": nid, "label": title, "path": path})
    title_to_id[title] = nid

# Build edges based on shared keywords between titles
titles = [e['title'] for e in meta]
for i, t1 in enumerate(titles):
    kw1 = keywords(t1)
    for j in range(i+1, len(titles)):
        t2 = titles[j]
        kw2 = keywords(t2)
        common = kw1 & kw2
        if common:
            edges.append({
                "source": title_to_id[t1],
                "target": title_to_id[t2],
                "weight": len(common)
            })

graph = {"nodes": nodes, "links": edges}
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(graph, f, indent=2)
print(f'✅ Graph generated with {len(nodes)} nodes and {len(edges)} links → {OUT_PATH}')
