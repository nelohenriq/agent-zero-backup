"""Slack integration for posting knowledge base summaries."""
import aiohttp
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackNotifier:
 """Posts summaries to Slack channel."""
 
 def __init__(self, webhook_url: str):
 self.webhook_url = webhook_url
 
 async def send_summary(self, result: Dict):
 """Send a formatted summary to Slack."""
 if not self.webhook_url:
 return
 
 title = result.get("title", "Untitled")[:80]
 url = result.get("url", "")
 source_type = result.get("source_type", "article")
 entities = result.get("entities", {})
 author = result.get("author", "")
 summary = result.get("summary", "")[:300]
 
 entity_list = []
 for etype, enames in entities.items():
 if etype in ["people", "organizations", "companies"]:
 entity_list.extend(enames[:3])
 entity_str = ", ".join(entity_list[:5]) if entity_list else "None extracted"
 
 source_emoji = {
 "youtube": "📺",
 "twitter": "🐦",
 "article": "📰",
 "pdf": "📄"
 }.get(source_type, "📎")
 
 payload = {
 "text": f"{source_emoji} *New Knowledge Added*",
 "blocks": [
 {
 "type": "header",
 "text": {
 "type": "plain_text",
 "text": f"{source_emoji} {title}"
 }
 },
 {
 "type": "section",
 "fields": [
 {"type": "mrkdwn", "text": f"*Type:* {source_type}"},
 {"type": "mrkdwn", "text": f"*Author:* {author or 'Unknown'}"}
 ]
 },
 {
 "type": "section",
 "text": {
 "type": "mrkdwn",
 "text": f"*Key Entities:* {entity_str}"
 }
 },
 {
 "type": "section",
 "text": {
 "type": "mrkdwn",
 "text": f"*Summary:* {summary}..."
 }
 },
 {
 "type": "actions",
 "elements": [
 {
 "type": "button",
 "text": {"type": "plain_text", "text": "View Source"},
 "url": url
 }
 ]
 }
 ]
 }
 
 try:
 async with aiohttp.ClientSession() as session:
 async with session.post(self.webhook_url, json=payload) as resp:
 if resp.status != 200:
 logger.error(f"Slack webhook failed: {resp.status}")
 else:
 logger.info("Posted summary to Slack")
 except Exception as e:
 logger.error(f"Error posting to Slack: {e}")
 
 async def send_digest(self, items: List[Dict]):
 """Send a daily/weekly digest of new items."""
 if not items:
 return
 
 blocks = [
 {
 "type": "header",
 "text": {
 "type": "plain_text",
 "text": f"📚 Knowledge Digest - {datetime.now().strftime('%Y-%m-%d')}"
 }
 }
 ]
 
 for item in items[:10]:
 title = item.get("title", "Untitled")[:60]
 url = item.get("url", "")
 source_type = item.get("source_type", "")
 
 blocks.append({
 "type": "section",
 "text": {
 "type": "mrkdwn",
 "text": f"• <{url}|{title}> ({source_type})"
 }
 })
 
 payload = {"text": "Knowledge digest", "blocks": blocks}
 
 try:
 async with aiohttp.ClientSession() as session:
 async with session.post(self.webhook_url, json=payload) as resp:
 logger.info(f"Digest sent: {resp.status}")
 except Exception as e:
 logger.error(f"Error sending digest: {e}")
