## [LRN-20260311-001] best_practice

**Logged**: 2026-03-11T10:11:37Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Successfully retrieved YouTube transcript using youtube-transcript-api directly instead of relying on project's ingest pipeline

### Details
User requested full transcript of video MoKNM53PLS4. Previous attempts using memory_load and document_query failed because:
1. The /ingest Telegram command was not properly storing transcript content
2. Knowledge directories (solutions/, fragments/, main/) were empty despite previous /ingest attempts
3. The youtube_url_watcher.py has compatibility issues with newer YouTubeTranscriptApi (dict vs attribute access)

The successful approach:
1. Used pip install youtube-transcript-api to ensure library available
2. Changed from dict-style access (segment["text"]) to attribute-style (segment.text) to match current API
3. Retrieved transcript directly from YouTube API
4. Saved to knowledge directory manually

### Suggested Action
- Fix telegram_handler.py /ingest command to properly process YouTube URLs
- Update youtube_url_watcher.py for API compatibility
- Add proper error handling and feedback when content fails to store
- Document this pattern: when project ingest fails, use direct library API as fallback

### Metadata
- Source: error
- Related Files:
  - src/bot/telegram_handler.py
  - src/fetchers/youtube_url_watcher.py
  - .a0proj/knowledge/main/youtube/openclaw_release_update_20260311.md
- Tags: youtube, transcript, ingestion, api-compatibility
- See Also: LRN-20260311-002 (telegram /ingest fix)
- Pattern-Key: harden.api_compatibility_check

---
## [LRN-20260311-001] best_practice

**Logged**: 2026-03-11T10:11:37Z
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
Successfully retrieved YouTube transcript using youtube-transcript-api directly instead of relying on project's ingest pipeline

### Details
User requested full transcript of video MoKNM53PLS4. Previous attempts using memory_load and document_query failed because:
1. The /ingest Telegram command was not properly storing transcript content
2. Knowledge directories (solutions/, fragments/, main/) were empty despite previous /ingest attempts
3. The youtube_url_watcher.py has compatibility issues with newer YouTubeTranscriptApi (dict vs attribute access)

The successful approach:
1. Used pip install youtube-transcript-api to ensure library available
2. Changed from dict-style access (segment["text"]) to attribute-style (segment.text) to match current API
3. Retrieved transcript directly from YouTube API
4. Saved to knowledge directory manually

### Solution Applied
Transcript saved to: .a0proj/knowledge/main/youtube/openclaw_release_update_20260311.md

### Suggested Action
- Fix telegram_handler.py /ingest command to properly process YouTube URLs
- Update youtube_url_watcher.py for API compatibility
- Add proper error handling and feedback when content fails to store
- Document this pattern: when project ingest fails, use direct library API as fallback

### Metadata
- Source: error
- Related Files:
 - src/bot/telegram_handler.py
 - src/fetchers/youtube_url_watcher.py
 - .a0proj/knowledge/main/youtube/openclaw_release_update_20260311.md
- Tags: youtube, transcript, ingestion, api-compatibility
- See Also: LRN-20260311-002 (telegram /ingest fix)
- Pattern-Key: harden.api_compatibility_check

---
