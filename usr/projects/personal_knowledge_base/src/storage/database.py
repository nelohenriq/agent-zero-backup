"""SQLite database storage."""
import sqlite3
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
 """SQLite database manager."""

 def __init__(self, db_path: str):
 self.db_path = db_path
 os.makedirs(os.path.dirname(db_path), exist_ok=True)
 self._init_db()

 def _init_db(self):
 """Initialize database schema."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()

 # Sources table
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS sources (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 url TEXT UNIQUE NOT NULL,
 title TEXT,
 source_type TEXT NOT NULL,
 content TEXT,
 metadata TEXT,
 ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 )
 """)

 # Chunks table
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS chunks (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 source_id INTEGER NOT NULL,
 content TEXT NOT NULL,
 chunk_index INTEGER,
 embedding TEXT,
 FOREIGN KEY (source_id) REFERENCES sources(id)
 )
 """)

 # Entities table
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS entities (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 entity_type TEXT NOT NULL,
 UNIQUE(name, entity_type)
 )
 """)

 # Entity mentions table
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS entity_mentions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 entity_id INTEGER NOT NULL,
 source_id INTEGER NOT NULL,
 FOREIGN KEY (entity_id) REFERENCES entities(id),
 FOREIGN KEY (source_id) REFERENCES sources(id)
 )
 """)

 # Create indexes
 cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_url ON sources(url)")
 cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id)")
 cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")
 cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_mentions_entity ON entity_mentions(entity_id)")
 cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_mentions_source ON entity_mentions(source_id)")

 conn.commit()
 conn.close()
 logger.info(f"Database initialized at {self.db_path}")

 def add_source(self, url: str, title: str, source_type: str, content: str, metadata: Dict = None) -> int:
 """Add a new source."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 cursor.execute("""
 INSERT OR REPLACE INTO sources (url, title, source_type, content, metadata)
 VALUES (?, ?, ?, ?, ?)
 """, (url, title, source_type, content, json.dumps(metadata or {})))
 source_id = cursor.lastrowid
 conn.commit()
 conn.close()
 return source_id

 def add_chunk(self, source_id: int, content: str, chunk_index: int) -> int:
 """Add a content chunk."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 cursor.execute("""
 INSERT INTO chunks (source_id, content, chunk_index)
 VALUES (?, ?, ?)
 """, (source_id, content, chunk_index))
 chunk_id = cursor.lastrowid
 conn.commit()
 conn.close()
 return chunk_id

 def update_chunk_embedding(self, chunk_id: int, embedding) -> None:
 """Update chunk embedding."""
 import numpy as np
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 emb_json = json.dumps(embedding.tolist() if isinstance(embedding, np.ndarray) else embedding)
 cursor.execute("UPDATE chunks SET embedding = ? WHERE id = ?", (emb_json, chunk_id))
 conn.commit()
 conn.close()

 def add_entity(self, name: str, entity_type: str, source_id: int) -> int:
 """Add an entity and link to source."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 cursor.execute("INSERT OR IGNORE INTO entities (name, entity_type) VALUES (?, ?)", (name, entity_type))
 cursor.execute("SELECT id FROM entities WHERE name = ? AND entity_type = ?", (name, entity_type))
 entity_id = cursor.fetchone()[0]
 cursor.execute("INSERT OR IGNORE INTO entity_mentions (entity_id, source_id) VALUES (?, ?)", (entity_id, source_id))
 conn.commit()
 conn.close()
 return entity_id

 def get_source(self, source_id: int) -> Optional[Dict[str, Any]]:
 """Get source by ID."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
 row = cursor.fetchone()
 conn.close()
 if row:
 return {
 "id": row[0], "url": row[1], "title": row[2],
 "source_type": row[3], "content": row[4],
 "metadata": json.loads(row[5]) if row[5] else {},
 "ingested_at": row[6]
 }
 return None

 def get_source_entities(self, source_id: int) -> Dict[str, List[str]]:
 """Get entities for a source."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 cursor.execute("""
 SELECT e.name, e.entity_type FROM entities e
 JOIN entity_mentions em ON e.id = em.entity_id WHERE em.source_id = ?
 """, (source_id,))
 entities = {"people": [], "organizations": [], "concepts": []}
 for row in cursor.fetchall():
 name, entity_type = row
 if entity_type in entities:
 entities[entity_type].append(name)
 elif entity_type == "company":
 entities["organizations"].append(name)
 conn.close()
 return entities

 def delete_source(self, source_id: int) -> bool:
 """Delete a source and its chunks."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 cursor.execute("DELETE FROM chunks WHERE source_id = ?", (source_id,))
 cursor.execute("DELETE FROM entity_mentions WHERE source_id = ?", (source_id,))
 cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
 deleted = cursor.rowcount > 0
 conn.commit()
 conn.close()
 return deleted

 def get_stats(self) -> Dict[str, Any]:
 """Get database statistics."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 cursor.execute("SELECT COUNT(*) FROM sources")
 sources = cursor.fetchone()[0]
 cursor.execute("SELECT COUNT(*) FROM chunks")
 chunks = cursor.fetchone()[0]
 cursor.execute("SELECT COUNT(*) FROM entities")
 entities = cursor.fetchone()[0]
 cursor.execute("SELECT COUNT(*) FROM entity_mentions")
 mentions = cursor.fetchone()[0]
 conn.close()
 return {"sources": sources, "chunks": chunks, "entities": entities, "entity_mentions": mentions}

 def get_all_sources(self, source_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
 """Get all sources."""
 conn = sqlite3.connect(self.db_path)
 cursor = conn.cursor()
 if source_type:
 cursor.execute("""
 SELECT id, url, title, source_type, ingested_at
 FROM sources WHERE source_type = ? ORDER BY ingested_at DESC LIMIT ?
 """, (source_type, limit))
 else:
 cursor.execute("""
 SELECT id, url, title, source_type, ingested_at
 FROM sources ORDER BY ingested_at DESC LIMIT ?
 """, (limit,))
 rows = cursor.fetchall()
 conn.close()
 return [{"id": r[0], "url": r[1], "title": r[2], "source_type": r[3], "ingested_at": r[4]} for r in rows]