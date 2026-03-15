"""Configuration for the knowledge base."""
import os
from typing import Optional


class Config:
    """Application configuration."""
    
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.browser_profile_path = os.getenv(
            "BROWSER_PROFILE_PATH",
            "/root/.config/google-chrome"
        )
        self.db_path = os.getenv(
            "DB_PATH",
            "/a0/usr/projects/personal_knowledge_base/data/knowledge.db"
        )
        self.embeddings_model = os.getenv(
            "EMBEDDINGS_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
        self.time_boost = float(os.getenv("TIME_BOOST", "0.3"))
        self.source_boost = float(os.getenv("SOURCE_BOOST", "0.2"))
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment."""
        return cls()
