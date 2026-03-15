"""Semantic search engine with time-aware and source-weighted ranking."""
import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os


class SemanticSearchEngine:
    """Semantic search with ranking boosts."""

    def __init__(self, db_path: str, embedding_dim: int = 384):
        self.db_path = db_path
        self.embedding_dim = embedding_dim

    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        filters: Dict[str, Any] = None,
        time_boost: float = 0.3,
        source_boost: float = 0.2
    ) -> List[Dict[str, Any]]:
        """Search with time-aware and source-weighted ranking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query_parts = ["SELECT id, source_id, content, embedding FROM chunks WHERE embedding IS NOT NULL"]
        params = []

        if filters:
            if filters.get("source_type"):
                query_parts.append("""
                AND source_id IN (SELECT id FROM sources WHERE source_type = ?)
                """)
                params.append(filters["source_type"])

        cursor.execute(" ".join(query_parts), params)
        chunks = cursor.fetchall()

        results = []
        for chunk_id, source_id, content, emb_json in chunks:
            chunk_embedding = np.array(json.loads(emb_json))
            similarity = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding) + 1e-8
            )

            cursor.execute("""
            SELECT url, title, source_type, ingested_at FROM sources WHERE id = ?
            """, (source_id,))
            source = cursor.fetchone()

            if source:
                url, title, source_type, ingested_at = source

                time_score = self._compute_time_score(ingested_at)
                source_score = self._compute_source_score(source_type)

                final_score = similarity + time_boost * time_score + source_boost * source_score

                results.append({
                    "chunk_id": chunk_id,
                    "source_id": source_id,
                    "content": content,
                    "score": float(final_score),
                    "similarity": float(similarity),
                    "time_score": float(time_score),
                    "source_score": float(source_score),
                    "url": url,
                    "title": title,
                    "source_type": source_type
                })

        conn.close()
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _compute_time_score(self, ingested_at: str) -> float:
        """Compute time-based score (more recent = higher score)."""
        try:
            ingested_dt = datetime.fromisoformat(ingested_at.replace("Z", "+00:00"))
            days_old = (datetime.now(ingested_dt.tzinfo) - ingested_dt).days
            return 1.0 / (1.0 + days_old / 30.0)
        except Exception:
            return 0.5

    def _compute_source_score(self, source_type: str) -> float:
        """Compute source-type score."""
        source_weights = {
            "article": 1.0,
            "youtube": 0.9,
            "twitter": 0.7,
            "pdf": 0.8
        }
        return source_weights.get(source_type, 0.5)

    def search_by_entity(
        self,
        entity: str,
        entity_type: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search sources by entity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT DISTINCT s.id, s.url, s.title, s.source_type, s.ingested_at
        FROM sources s
        JOIN entity_mentions em ON s.id = em.source_id
        JOIN entities e ON em.entity_id = e.id
        WHERE e.name LIKE ?
        """
        params = [f"%{entity}%"]

        if entity_type:
            query += " AND e.entity_type = ?"
            params.append(entity_type)

        query += " ORDER BY s.ingested_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "url": row[1],
                "title": row[2],
                "source_type": row[3],
                "ingested_at": row[4]
            }
            for row in results
        ]
