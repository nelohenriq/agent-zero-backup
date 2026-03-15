# Shared Knowledge Base (Project‑agnostic)

## What it provides
- **One place** (`/a0/usr/shared_knowledge`) for all SearXNG web‑search results.
- Automatic markdown storage, import manifest (`knowledge_import.json`) and shared FAISS index.
- Simple **graph generator** (`graph_generator.py`) that creates `graph.json`.
- Minimal **frontend** (`webapp/app.py`) exposing the graph via D3.js on `http://localhost:5560`.

## Typical workflow
1. **Run a search** (from any project or directly):
   ```bash
   python /a0/usr/shared_knowledge/fetch_and_store.py "shift worker productivity hacks"
   ```
   This writes markdown files to the shared `web/` folder, updates the manifest and re‑indexes FAISS.
2. **Generate / update the knowledge graph**:
   ```bash
   python /a0/usr/shared_knowledge/graph_generator.py
   ```
3. **View the graph**:
   ```bash
   python /a0/usr/shared_knowledge/webapp/app.py
   ```
   Then open `http://<container‑ip>:5560` in a browser.
4. **Use the knowledge base** in any project by pointing your retrieval code to the shared FAISS files:
   - `index.faiss` → `/a0/usr/shared_knowledge/.a0proj/memory/index.faiss`
   - `index.pkl`   → `/a0/usr/shared_knowledge/.a0proj/memory/index.pkl`
   - `knowledge_import.json` stays the same.

## Adding the shared store to an existing project
You can keep your project‑specific knowledge as before, but for global searches import the shared manifest:
```python
from langchain.vectorstores import FAISS
# load shared index
vector_store = FAISS.load_local('/a0/usr/shared_knowledge/.a0proj/memory', embeddings)
```

Feel free to adapt the scripts (e.g., enhance edge creation, add tags, change the visual style).
