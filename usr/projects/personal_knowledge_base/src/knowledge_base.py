"""Main Knowledge Base class."""
import os
import json
import numpy as np
from typing import Dict, List, Any, Optional

from config import Config
from storage.database import Database
from storage.embeddings import EmbeddingStorage
from processors.entity_extractor import EntityExtractor
from search.semantic_search import SemanticSearchEngine
from fetchers.content_fetchers import ContentFetcher


class KnowledgeBase:
 """Personal knowledge base with RAG."""

    def __init__(self, config: Config = None):
        self.config = config or Config.from_env()
        self.db = Database(self.config.db_path)
        self.embedding_storage = EmbeddingStorage(self.config.db_path)
        self.entity_extractor = EntityExtractor()
        self.search_engine = SemanticSearchEngine(self.config.faiss_index_path)
        self.content_fetcher = ContentFetcher()
        self._embedding_model = None

 @property
 def embedding_model(self):
 """Lazy load embedding model."""
 if self._embedding_model is None:
 from sentence_transformers import SentenceTransformer
    self._embedding_model = SentenceTransformer(self.config.embeddings_model)
 return self._embedding_model

 def ingest_url(self, url: str) -> Dict[str, Any]:
 """Ingest content from a URL."""
 result = self.content_fetcher.fetch(url)

 if not result or not result.get("content"):
 return {"success": False, "error": "Failed to fetch content"}

 source_id = self.db.add_source(
 url=url,
 title=result.get("title", "Untitled"),
 source_type=result.get("source_type", "article"),
 content=result["content"],
 metadata=result.get("metadata", {})
 )

 chunks = self._chunk_text(result["content"])

 for i, chunk in enumerate(chunks):
 chunk_id = self.db.add_chunk(source_id, chunk, i)
 embedding = self.embedding_model.encode(chunk)
    self.db.update_chunk_embedding(chunk_id, embedding)
    self.embedding_storage.add_embedding(chunk_id, embedding)

 entities = self.entity_extractor.extract(result["content"])
 for entity_type, entity_list in entities.items():
 for entity in entity_list:
    self.db.add_entity(entity, entity_type, source_id)

 return {
 "success": True,
 "source_id": source_id,
 "title": result.get("title"),
 "chunks": len(chunks),
 "entities": entities
 }

 def _chunk_text(self, text: str) -> List[str]:
 """Split text into chunks."""
 words = text.split()
 chunks = []
 current_chunk = []
 current_length = 0

 for word in words:
 if current_length + len(word) > self.config.chunk_size:
 if current_chunk:
 chunks.append(" ".join(current_chunk))
 overlap_words = current_chunk[-self.config.chunk_overlap // 5:] if self.config.chunk_overlap > 0 else []
 current_chunk = overlap_words + [word]
 current_length = len(" ".join(current_chunk))
 else:
 current_chunk.append(word)
 current_length += len(word) + 1

 if current_chunk:
 chunks.append(" ".join(current_chunk))

 return chunks

 def query(
 self,
 query_text: str,
 limit: int = 10,
 filters: Dict[str, Any] = None
 ) -> List[Dict[str, Any]]:
 """Search the knowledge base."""
 query_embedding = self.embedding_model.encode(query_text)

 results = self.search_engine.search(
 query_embedding,
 limit=limit,
 filters=filters,
 time_boost=self.config.time_boost,
 source_boost=self.config.source_boost
 )

 return results

 def query_by_entity(
 self,
 entity: str,
 entity_type: str = None,
 limit: int = 10
 ) -> List[Dict[str, Any]]:
 """Search by entity."""
 return self.search_engine.search_by_entity(entity, entity_type, limit)

 def get_source(self, source_id: int) -> Optional[Dict[str, Any]]:
 """Get source details."""
 source = self.db.get_source(source_id)
 if source:
 source["entities"] = self.db.get_source_entities(source_id)
 return source
 return None

 def delete_source(self, source_id: int) -> bool:
 """Delete a source."""
 return self.db.delete_source(source_id)

 def get_stats(self) -> Dict[str, Any]:
 """Get knowledge base statistics."""
 return self.db.get_stats()

 def list_sources(
 self,
 source_type: str = None,
 limit: int = 100
 ) -> List[Dict[str, Any]]:
 """List all sources."""
 return self.db.get_all_sources(source_type, limit)
