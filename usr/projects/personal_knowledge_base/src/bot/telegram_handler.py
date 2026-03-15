"""Telegram bot handler for URL ingestion."""
import asyncio
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update, Bot
from telegram.ext import (
    Application, 
    CommandHandler,
    MessageHandler, 
    filters, 
    ContextTypes
)
from telegram.request import HTTPXRequest

logger = logging.getLogger(__name__)


class TelegramURLWatcher:
    """Watches a Telegram for URLs and processes them."""
    
    URL_PATTERN = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    
    def __init__(self, token: str, topic_chat_id: int, topic_thread_id: int,
                 knowledge_base, slack_notifier=None):
        self.token = token
        self.topic_chat_id = topic_chat_id
        self.topic_thread_id = topic_thread_id
        self.knowledge_base = knowledge_base
        self.slack_notifier = slack_notifier
        self.app = None
        self.stats = {"processed": 0, "errors": 0}

    async def start(self):
        """Initialize and start the bot with all handlers registered."""
        request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
        self.app = Application.builder().token(self.token).request(request).build()
        
        # Register ALL command handlers (CRITICAL FIX - these were missing!)
        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("ingest", self._handle_ingest_command))
        self.app.add_handler(CommandHandler("query", self._handle_query_command))
        self.app.add_handler(CommandHandler("restart", self._handle_restart))
        
        # Register message handler for URL detection in topics
        self.app.add_handler(
            MessageHandler(
                filters.Chat(self.topic_chat_id) & filters.TEXT & ~filters.COMMAND,
                self._handle_message
            )
        )
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        logger.info(f"Telegram bot started. Watching chat {self.topic_chat_id}")

    async def stop(self):
        """Stop the bot gracefully."""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with bot instructions."""
        help_text = (
            "🤖 *Personal Knowledge Bot*\n\n"
            "*Commands:*\n"
            "/ingest <URL> - Add a URL to knowledge base\n"
            "/query <text> - Search the knowledge base\n"
            "/restart - Restart the bot\n\n"
            "*Usage:*\n"
            "/ingest https://youtube.com/watch?v=...\n"
            "/query post-compaction\n\n"
            "*Features:*\n"
            "- Articles, YouTube, X/Twitter, PDFs\n"
            "- Semantic search with time/entity boosts"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def _handle_restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /restart command."""
        await update.message.reply_text("♻️ Restarting bot...")
        logger.info("Restart requested via Telegram")
        # Note: Restart requires external process management

    async def _handle_ingest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ingest <URL> command directly to the bot."""
        if len(context.args) != 1:
            await update.message.reply_text(
                "📌 Usage: `/ingest <URL>`\n"
                "Example: `/ingest https://youtube.com/watch?v=MoKNM53PLS4`",
                parse_mode="Markdown"
            )
            return

        url = context.args[0]
        user = update.message.from_user.username or "Unknown"
        
        # Send processing message
        processing_msg = await update.message.reply_text("⏳ Processing URL...")
        
        try:
            # CRITICAL FIX: Added await (was missing!)
            result = await self._process_url(url, user)
            
            await processing_msg.edit_text(
                f"✅ *Ingested:* {result['title'][:50]}...\n"
                f"*Type:* `{result['source_type']}`\n"
                f"*Path:* `{result.get('stored_path', 'N/A')}`",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error in /ingest: {e}", exc_info=True)
            await processing_msg.edit_text(f"❌ Error: `{str(e)[:200]}`", parse_mode="Markdown")

    async def _handle_query_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /query <text> – search the knowledge base and reply."""
        query = " ".join(context.args).strip()
        if not query:
            await update.message.reply_text(
                "🤖 *Query the knowledge base*\n\n"
                "Usage:\n```/query <your question>```\n\n"
                "Example:\n```/query post-compaction```",
                parse_mode="Markdown"
            )
            return

        try:
            hits = await self.knowledge_base.search(query, top_k=5)

            if not hits:
                await update.message.reply_text("🔍 No matches found.")
                return

            lines = [f"🔍 *Results for:* `{query}`\n"]
            for i, (title, snippet, score) in enumerate(hits, 1):
                lines.append(
                    f"\n[{i}] *{self._escape_markdown(title[:60])}*\n"
                    f"> {self._escape_markdown(snippet[:150])}…\n"
                    f"_score: {score:.2f}_"
                )
            
            reply_text = "\n".join(lines)
            # Telegram has 4096 char limit
            if len(reply_text) > 4000:
                reply_text = reply_text[:4000] + "\n\n_(truncated)_"
                
            await update.message.reply_text(reply_text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Query error: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Query failed: {str(e)[:200]}")

    def _escape_markdown(self, text: str) -> str:
        """Escape special MarkdownV2 characters."""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f"\\{char}")
        return text

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages containing URLs in configured topic."""
        message = update.effective_message
        if not message or not message.text:
            return

        message_thread_id = message.message_thread_id
        if self.topic_thread_id and message_thread_id != self.topic_thread_id:
            return

        urls = self._extract_urls(message.text)
        if not urls:
            return

        user = message.from_user.username or "Unknown"
        logger.info(f"Received {len(urls)} URLs from {user}")

        for url in urls:
            try:
                result = await self._process_url(url, user)
                
                reply_text = (
                    f"✅ *Processed:* {result['title'][:50]}...\n"
                    f"*Type:* `{result['source_type']}`\n"
                    f"*Entities:* {len(result.get('entities', {}))}\n"
                    f"*Stored:* `{result.get('stored_path', 'N/A')}`"
                )
                
                await message.reply_text(reply_text, parse_mode="Markdown", 
                                       message_thread_id=message_thread_id)

                if self.slack_notifier and result.get('entities'):
                    await self.slack_notifier.send_summary(result)

                self.stats["processed"] += 1
            except Exception as e:
                logger.error(f"Error processing {url}: {e}", exc_info=True)
                self.stats["errors"] += 1
                await message.reply_text(
                    f"❌ Error processing URL: `{str(e)[:150]}`",
                    parse_mode="Markdown",
                    message_thread_id=message_thread_id
                )

    def _extract_urls(self, text: str) -> List[str]:
        """Extract and clean URLs from text."""
        urls = re.findall(self.URL_PATTERN, text)
        clean_urls = []
        for url in urls:
            if not url.startswith('http'):
                url = 'https://' + url
            url = re.sub(r'[.,!?;:]$', '', url)
            clean_urls.append(url)
        return list(set(clean_urls))

    async def _process_url(self, url: str, user: str) -> Dict:
        """Process a URL through the knowledge base ingestion pipeline."""
        result = await self.knowledge_base.ingest_url(url, ingested_by=user)
        
        if isinstance(result, dict) and "error" in result:
            raise Exception(result["error"])
        
        result["ingested_by"] = user
        result["ingested_at"] = datetime.now().isoformat()
        return result

    def run_sync(self):
        """Run the bot synchronously."""
        asyncio.run(self._run_async())

    async def _run_async(self):
        """Main async loop."""
        await self.start()
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            pass
        finally:
            await self.stop()


class KnowledgeBaseBot:
    """Main bot class - DEPRECATED, use TelegramURLWatcher directly."""
    
    def __init__(self, telegram_token: str, telegram_chat_id: int,
                 telegram_thread_id: int, knowledge_base, slack_webhook: str = None):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_thread_id = telegram_thread_id
        self.knowledge_base = knowledge_base
        self.slack_webhook = slack_webhook
        self.watcher = TelegramURLWatcher(
            telegram_token,
            telegram_chat_id,
            telegram_thread_id,
            knowledge_base,
            SlackNotifier(slack_webhook) if slack_webhook else None
        )

    def start(self):
        """Start the bot."""
        self.watcher.run_sync()

    def stop(self):
        """Stop the bot."""
        asyncio.run(self.watcher.stop())


class SlackNotifier:
    """Simple Slack webhook notifier."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_summary(self, result: Dict):
        """Send entity summary to Slack."""
        import aiohttp
        
        entities = result.get("entities", {})
        if not entities:
            return
        
        payload = {
            "text": f"📚 New ingestion: *{result.get('title', 'Unknown')}*\n"
                    f"*Entities:* {', '.join(list(entities.keys())[:10])}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status != 200:
                        logger.warning(f"Slack notification failed: {resp.status}")
        except Exception as e:
            logger.error(f"Slack notification error: {e}")
