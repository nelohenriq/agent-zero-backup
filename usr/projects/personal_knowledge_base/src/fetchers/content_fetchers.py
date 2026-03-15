"""Content fetchers for different URL types."""
import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, List, Optional
import json


class URLDetector:
    """Detect the type of URL and extract relevant IDs."""
    
    @staticmethod
    def detect_type(url: str) -> str:
        url_lower = url.lower()
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return "twitter"
        elif url_lower.endswith(".pdf") or "pdf" in url_lower:
            return "pdf"
        else:
            return "article"
    
    @staticmethod
    def extract_youtube_id(url: str) -> Optional[str]:
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})"
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def extract_tweet_id(url: str) -> Optional[str]:
        match = re.search(r"(?:twitter\.com|x\.com)/\w+/status/(\d+)", url)
        if match:
            return match.group(1)
        return None


class ArticleFetcher:
    """Fetch content from web articles."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def fetch(self, url: str) -> Dict:
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            title = soup.find("title").get_text().strip() if soup.find("title") else ""
            
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            article = soup.find("article") or soup.find("main") or soup.find("body")
            content = article.get_text(separator=" ", strip=True) if article else ""
            
            content = re.sub(r"\s+", " ", content)
            
            author = ""
            author_tag = soup.find("meta", attrs={"name": "author"})
            if author_tag:
                author = author_tag.get("content", "")
            
            published = ""
            date_tag = soup.find("meta", attrs={"property": "article:published_time"})
            if date_tag:
                published = date_tag.get("content", "")
            
            return {
                "title": title,
                "content": content,
                "author": author,
                "published_date": published,
                "url": url
            }
        except Exception as e:
            return {"error": str(e), "url": url}


class YouTubeFetcher:
    """Fetch transcripts from YouTube videos."""
    
    def fetch(self, url: str) -> Dict:
        video_id = URLDetector.extract_youtube_id(url)
        if not video_id:
            return {"error": "Could not extract YouTube video ID", "url": url}
        
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id)
            transcript_text = " ".join([entry.text for entry in transcript_list])
            
            video_info = self._get_video_info(video_id)
            
            return {
                "title": video_info.get("title", ""),
                "content": transcript_text,
                "author": video_info.get("author_name", ""),
                "published_date": "",
                "url": url,
                "video_id": video_id
            }
        except Exception as e:
            return {"error": str(e), "url": url}
    
    def _get_video_info(self, video_id: str) -> Dict:
        try:
            import urllib.request
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            with urllib.request.urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode())
        except:
            return {}


class TwitterFetcher:
    """Fetch tweets and threads from Twitter/X."""
    
    def __init__(self, bearer_token=None):
        self.bearer_token = bearer_token
    
    def fetch_tweet(self, url: str) -> Dict:
        tweet_id = URLDetector.extract_tweet_id(url)
        if not tweet_id:
            return {"error": "Could not extract tweet ID", "url": url}
        
        try:
            return self._fetch_scrape(url)
        except Exception as e:
            return {"error": str(e), "url": url}
    
    def fetch_thread(self, url: str) -> Dict:
        """Fetch entire Twitter thread by scraping."""
        return self.fetch_tweet(url)
    
    def _fetch_scrape(self, url: str) -> Dict:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")
        
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else "Tweet"
        
        meta_desc = soup.find("meta", attrs={"property": "og:description"})
        content = meta_desc.get("content", "") if meta_desc else ""
        
        return {
            "title": title,
            "content": content,
            "author": "",
            "published_date": "",
            "url": url
        }
    
    def find_linked_urls(self, content: str) -> List[str]:
        """Find URLs linked in tweet content."""
        url_pattern = r"https?://[^\s]+"
        return re.findall(url_pattern, content)


class PDFFetcher:
    """Fetch content from PDF files."""
    
    def fetch(self, url: str) -> Dict:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            import io
            from PyPDF2 import PdfReader
            
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            content = "\n".join(text_parts)
            title = url.split("/")[-1].replace(".pdf", "")
            
            return {
                "title": title,
                "content": content,
                "author": "",
                "published_date": "",
                "url": url
            }
        except ImportError:
            return {"error": "PyPDF2 not installed", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}


class ContentFetcher:
    """Main fetcher that routes to appropriate fetcher based on URL type."""
    
    def __init__(self, twitter_bearer_token=None):
        self.article_fetcher = ArticleFetcher()
        self.youtube_fetcher = YouTubeFetcher()
        self.twitter_fetcher = TwitterFetcher(twitter_bearer_token)
        self.pdf_fetcher = PDFFetcher()
    
    def fetch(self, url: str, fetch_thread: bool = True) -> Dict:
        url_type = URLDetector.detect_type(url)
        
        if url_type == "youtube":
            return self.youtube_fetcher.fetch(url)
        elif url_type == "twitter":
            if fetch_thread:
                return self.twitter_fetcher.fetch_thread(url)
            else:
                return self.twitter_fetcher.fetch_tweet(url)
        elif url_type == "pdf":
            return self.pdf_fetcher.fetch(url)
        else:
            return self.article_fetcher.fetch(url)
    
    def fetch_linked_articles(self, tweet_content: str) -> List[Dict]:
        """Fetch articles linked in a tweet."""
        linked_urls = self.twitter_fetcher.find_linked_urls(tweet_content)
        articles = []
        for linked_url in linked_urls:
            if not any(x in linked_url.lower() for x in ["twitter.com", "x.com", "t.co"]):
                article = self.article_fetcher.fetch(linked_url)
                if "error" not in article:
                    articles.append(article)
        return articles
