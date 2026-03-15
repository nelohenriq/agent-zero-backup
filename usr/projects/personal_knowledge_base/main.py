#!/usr/bin/env python3
"""Main entry point for the Personal Knowledge Base."""
import os
import sys
import argparse
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_path():
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def create_kb(config_override: dict = None):
    setup_path()
    from config import Config
    from knowledge_base import KnowledgeBase

    config = Config()
    if config_override:
        for key, value in config_override.items():
            config[key] = value

    return KnowledgeBase(
        db_path=config.db_path,
        embeddings_model=config.embeddings_model,
        browser_profile_path=config.get("browser_profile_path")
    )


def cmd_ingest(args):
    """Ingest a URL into the knowledge base."""
    kb = create_kb({"db_path": args.db_path} if args.db_path else None)

    for url in args.urls:
        logger.info(f"Ingesting: {url}")
        result = kb.ingest_url(url)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success: {result['title']}")
            print(f"   Type: {result['source_type']}")
            print(f"   Chunks: {result['chunks']}")
            print(f"   Entities: {len(result.get('entities', {}))}")


def cmd_query(args):
    """Query the knowledge base."""
    kb = create_kb({"db_path": args.db_path} if args.db_path else None)

    filters = None
    if args.source_type:
        filters = {"source_type": args.source_type}

    result = kb.query(args.query, limit=args.limit, filters=filters)

    print(f"\n📚 Query: {args.query}")
    print(f"Found {result['total']} results\n")

    for i, r in enumerate(result['results'], 1):
        print(f"[{i}] {r['title']} (Score: {r['score']:.3f})")
        print(f"    Type: {r['source_type']} | URL: {r['url']}")
        print(f"    Content: {r['content'][:200]}...")
        print()


def cmd_search_entity(args):
    """Search by entity."""
    kb = create_kb({"db_path": args.db_path} if args.db_path else None)

    results = kb.search_engine.search_by_entity(args.entity, args.entity_type, args.limit)

    print(f"\n🏷️ Entity: {args.entity}")
    print(f"Found {len(results)} sources\n")

    for r in results:
        print(f"• {r['title']}")
        print(f"  URL: {r['url']}")
        print()


def cmd_stats(args):
    """Show knowledge base statistics."""
    kb = create_kb({"db_path": args.db_path} if args.db_path else None)

    stats = kb.get_stats()

    print("\n📊 Knowledge Base Statistics")
    print("="*40)
    print(f"Total Sources: {stats['total_sources']}")
    print(f"Total Chunks: {stats['total_chunks']}")
    print("\nBy Type:")
    for source_type, count in stats['by_type'].items():
        print(f"  {source_type}: {count}")
    print()


def cmd_list(args):
    """List all sources."""
    kb = create_kb({"db_path": args.db_path} if args.db_path else None)

    sources = kb.get_all_sources(source_type=args.source_type, limit=args.limit)

    print(f"\n📋 Sources ({len(sources)} items)\n")

    for s in sources:
        print(f"[{s['id']}] {s['title']}")
        print(f"    Type: {s['source_type']} | URL: {s['url']}")
        print(f"    Ingested: {s['ingested_at']}")
        print()


def cmd_bot(args):
    """Start the Telegram bot."""
    setup_path()
    from config import Config
    from bot.telegram_handler import KnowledgeBaseBot

    config = Config()

    if not config.telegram_configured:
        print("❌ Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        sys.exit(1)

    kb = create_kb()

    bot = KnowledgeBaseBot(
        telegram_token=config["telegram_token"],
        telegram_chat_id=int(config["telegram_chat_id"]),
        telegram_thread_id=int(config["telegram_thread_id"]) if config.get("telegram_thread_id") else None,
        knowledge_base=kb,
        slack_webhook=config.get("slack_webhook")
    )

    print("🤖 Starting Telegram bot...")
    print(f"Watching chat: {config['telegram_chat_id']}")
    print("Press Ctrl+C to stop")

    try:
        bot.start()
    except KeyboardInterrupt:
        print("\nStopping...")
        bot.stop()


def cmd_delete(args):
    """Delete a source."""
    kb = create_kb({"db_path": args.db_path} if args.db_path else None)

    kb.delete_source(args.source_id)
    print(f"✅ Deleted source {args.source_id}")


def main():
    parser = argparse.ArgumentParser(
        description='Personal Knowledge Base with RAG',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    ingest_parser = subparsers.add_parser('ingest', help='Ingest URLs')
    ingest_parser.add_argument('urls', nargs='+', help='URLs to ingest')
    ingest_parser.add_argument('--db-path', help='Database path')

    query_parser = subparsers.add_parser('query', help='Query the knowledge base')
    query_parser.add_argument('query', help='Natural language query')
    query_parser.add_argument('--limit', type=int, default=5, help='Max results')
    query_parser.add_argument('--source-type', help='Filter by source type')
    query_parser.add_argument('--db-path', help='Database path')

    entity_parser = subparsers.add_parser('entity', help='Search by entity')
    entity_parser.add_argument('entity', help='Entity name to search')
    entity_parser.add_argument('--entity-type', help='Entity type (people, organizations, etc.)')
    entity_parser.add_argument('--limit', type=int, default=10, help='Max results')
    entity_parser.add_argument('--db-path', help='Database path')

    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--db-path', help='Database path')

    list_parser = subparsers.add_parser('list', help='List sources')
    list_parser.add_argument('--source-type', help='Filter by source type')
    list_parser.add_argument('--limit', type=int, default=50, help='Max results')
    list_parser.add_argument('--db-path', help='Database path')

    bot_parser = subparsers.add_parser('bot', help='Start Telegram bot')

    delete_parser = subparsers.add_parser('delete', help='Delete a source')
    delete_parser.add_argument('source_id', type=int, help='Source ID to delete')
    delete_parser.add_argument('--db-path', help='Database path')

    args = parser.parse_args()

    if args.command == 'ingest':
        cmd_ingest(args)
    elif args.command == 'query':
        cmd_query(args)
    elif args.command == 'entity':
        cmd_search_entity(args)
    elif args.command == 'stats':
        cmd_stats(args)
    elif args.command == 'list':
        cmd_list(args)
    elif args.command == 'bot':
        cmd_bot(args)
    elif args.command == 'delete':
        cmd_delete(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
