"""Embedding storage with FAISS index."""
import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import os
import faiss


class EmbeddingStorage:
    """Manage embeddings with FAISS index."""

    def __init__(self, db_path: str, embedding_dim: int = 384):
        self.db_path = db_path
        self.embedding_dim = embedding_dim
        self.index = None
        self._init_index()

    def _init_index(self):
        """Initialize or load FAISS index."""
        index_path = self.db_path.replace(".db", ".faiss")

        if os.path.exists(index_path):
            try:
                self.index = faiss.read_index(index_path)
            except Exception:
                self.index = faiss.IndexFlatIP(self.embedding_dim)
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

    def add_embedding(self, chunk_id: int, embedding: np.ndarray) -> None:
        """Add embedding to index."""
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

        embedding = embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(embedding)

        self.index.add(embedding)
        self._save_index()

    def search_similar(
        self,
        query_embedding: np.ndarray,
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """Search for similar embeddings."""
        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query_embedding)

        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)

        return [(int(idx), float(dist)) for idx, dist in zip(indices[0], distances[0])]

    def _save_index(self):
        """Save FAISS index to disk."""
        index_path = self.db_path.replace(".db", ".faiss")
        faiss.write_index(self.index, index_path)

    def get_embedding_count(self) -> int:
        """Get number of embeddings in index."""
        return self.index.ntotal if self.index else 0
