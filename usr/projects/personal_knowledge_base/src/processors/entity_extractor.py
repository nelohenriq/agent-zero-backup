"""Entity extraction using spaCy."""
import spacy
from typing import Dict, List, Set
from collections import Counter


class EntityExtractor:
 """Extract named entities from text."""

 def __init__(self, model_name: str = "en_core_web_sm"):
 try:
 self.nlp = spacy.load(model_name)
 except OSError:
 from spacy.cli import download
 download(model_name)
 self.nlp = spacy.load(model_name)

 def extract(self, text: str) -> Dict[str, List[str]]:
 """Extract entities from text."""
 if not text or len(text.strip()) == 0:
 return {"people": [], "organizations": [], "concepts": []}

 doc = self.nlp(text[:100000]) # Limit text length

 entities = {
 "people": [],
 "organizations": [],
 "concepts": []
 }

 for ent in doc.ents:
 if ent.label_ == "PERSON":
 entities["people"].append(ent.text)
 elif ent.label_ in ("ORG", "COMPANY"):
 entities["organizations"].append(ent.text)
 elif ent.label_ in ("GPE", "LOC", "EVENT", "WORK_OF_ART", "LAW"):
 entities["concepts"].append(ent.text)

 # Extract noun chunks as concepts
 for chunk in doc.noun_chunks:
 if len(chunk.text.split()) > 1:
 entities["concepts"].append(chunk.text)

 # Deduplicate and clean
 for key in entities:
 entities[key] = list(set(e.strip() for e in entities[key] if len(e.strip()) > 1))
 entities[key] = sorted(entities[key], key=len, reverse=True)[:20]

 return entities

 def get_top_entities(self, text: str, n: int = 10) -> Dict[str, List[str]]:
 """Get top N entities by frequency."""
 entities = self.extract(text)
 result = {}

 for entity_type, entity_list in entities.items():
 counter = Counter(entity_list)
 result[entity_type] = [e for e, _ in counter.most_common(n)]

 return result
