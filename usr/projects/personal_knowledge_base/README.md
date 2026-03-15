# Personal Knowledge Base with RAG

A powerful personal knowledge base system that ingests content from various sources, extracts entities, and provides semantic search with time-aware and source-weighted ranking.

## Features

- **Multi-source Ingestion**: Supports articles, YouTube videos, X/Twitter threads, and PDFs
- **Smart URL Detection**: Automatically detects content type and fetches appropriately
- **Thread Following**: Follows complete Twitter/X threads, not just the first tweet
- **Linked Content**: When a tweet links to an article, ingests both
- **Entity Extraction**: Extracts people, organizations, and concepts using spaCy
- **Vector Embeddings**: Uses sentence-transformers for semantic similarity
- **Time-Aware Ranking**: Recent sources rank higher in search results
- **Source-Weighted Ranking**: Boost results based on source type
- **Paywall Support**: Uses browser automation for paywalled content
- **Telegram Integration**: Drop URLs in a Telegram topic for automatic ingestion
- **Slack Notifications**: Optionally post summaries to Slack

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for entity extraction
python -m spacy download en_core_web_sm

# Install Playwright for browser automation (optional, for paywalled content)
playwright install chromium
```

## Configuration

Create a `config.json` file or use environment variables:

```json
{
 "db_path": "knowledge.db",
 "embeddings_model": "sentence-transformers/all-MiniLM-L6-v2",
 "telegram_token": "YOUR_BOT_TOKEN",
 "telegram_chat_id": "YOUR_CHAT_ID",
 "telegram_thread_id": "YOUR_THREAD_ID",
 "slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK",
 "browser_profile_path": "/path/to/chrome/profile",
 "chunk_size": 512,
 "chunk_overlap": 100,
 "time_boost": 0.3,
 "source_boost": 0.2
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Chat ID to monitor |
| `TELEGRAM_THREAD_ID` | Thread/Topic ID (optional) |
| `SLACK_WEBHOOK_URL` | Slack webhook URL |
| `CHROME_PROFILE_PATH` | Chrome profile for paywalled sites |
| `KB_DB_PATH` | Database path |
| `KB_EMBEDDINGS_MODEL` | Embeddings model name |
| `KB_LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) |

## Usage

### CLI Commands

```bash
# Ingest URLs
python main.py ingest https://example.com/article https://youtube.com/watch?v=xxx

# Query the knowledge base
python main.py query "artificial intelligence trends in 2024"

# Search by entity
python main.py entity "Elon Musk" --entity-type people

# Show statistics
python main.py stats

# List all sources
python main.py list

# Start Telegram bot
python main.py bot

# Delete a source
python main.py delete 123
```

### Telegram Bot

1. Create a Telegram bot using @BotFather
2. Get your chat ID by messaging @userinfobot
3. Set the environment variables:
 ```bash
 export TELEGRAM_BOT_TOKEN="your_bot_token"
 export TELEGRAM_CHAT_ID="your_chat_id"
 export TELEGRAM_THREAD_ID="your_thread_id" # optional
 ```
4. Start the bot:
 ```bash
 python main.py bot
 ```

5. Drop URLs in the configured Telegram topic. The bot will:
 - Detect content type
 - Fetch and process content
 - Extract entities
 - Store in knowledge base
 - Optionally post a summary to Slack

### Slack Integration

Set `SLACK_WEBHOOK_URL` to receive notifications when new content is ingested.

## Architecture

```
personal_knowledge_base/
├── src/
│ ├── bot/ # Telegram and Slack handlers
│ ├── fetchers/ # Content fetchers for different sources
│ ├── processors/ # Entity extraction and text processing
│ ├── search/ # Semantic search engine
│ ├── storage/ # SQLite and embedding storage
│ ├── config.py # Configuration management
│ └── knowledge_base.py # Main orchestrator
├── main.py # CLI entry point
└── requirements.txt
```

## API Usage

```python
from main import create_kb

kb = create_kb()

# Ingest a URL
result = kb.ingest_url("https://example.com/article")
print(f"Ingested: {result['title']}")

# Query the knowledge base
results = kb.query("machine learning applications", limit=5)
for r in results['results']:
 print(f"{r['title']}: {r['score']:.3f}")

# Search by entity
sources = kb.search_engine.search_by_entity("OpenAI", "organizations")
print(f"Found {len(sources)} sources mentioning OpenAI")
```

## License

MIT License
