
## [ERR-20260311-001] OpenRouter Rate Limit - Ingest Command

**Logged**: 2026-03-11T10:20:00Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
OpenRouter API returned 429 Too Many Requests during YouTube video ingestion attempt

### Error
```
litellm.exceptions.RateLimitError: RateLimitError: OpenrouterException - 
{"error":{"message":"Provider returned error","code":429,
"metadata":{"raw":"qwen/qwen3-coder:free is temporarily rate-limited upstream. 
Please retry shortly, or add your own key to accumulate your rate limits: 
https://openrouter.ai/settings/integrations","provider_name":"Venice","is_byok":false}},
"user_id":"user_2deXMadGG3FKReMOjNQqUKJFJNX"}
```

### Context
- User attempted to ingest YouTube video via Telegram /ingest command
- Multiple retry attempts failed with same error
- API calls were made via litellm proxy through OpenRouter's free tier

### Impact
- /ingest command completely non-functional for new content
- User unable to add new URLs to knowledge base

### Suggested Fix
1. Add fallback embedding model (local ollama, or paid OpenRouter key)
2. Implement retry logic with exponential backoff
3. Add user-friendly error message explaining rate limits, not raw API errors
4. Consider caching embeddings to reduce API calls
5. Support multiple providers and rotate on rate limit

### Metadata
- Reproducible: yes
- Related Files: 
 - src/knowledge_base.py
 - src/bot/telegram_handler.py
 - src/storage/embeddings.py
- Tags: rate-limit, openrouter, api, embedding, ingestion
- See Also: ERR-20260311-002 (NotFoundError)

---

## [ERR-20260311-002] OpenRouter NotFoundError - Model Access

**Logged**: 2026-03-11T10:25:00Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
After rate limit resolved, ingestion still failed with NotFoundError 
"No endpoints found matching your data policy (Free model publication)"

### Error
```
litellm.exceptions.NotFoundError: No endpoints found matching your data policy 
(Free model publication). Modify options at: https://openrouter.ai/settings/integrations
```

### Context
- Same embedding operation after rate limit cleared
- OpenRouter free tier no longer providing access to qwen/qwen3-coder:free
- Model access policy changed on OpenRouter side

### Impact
- Complete breakdown of embedding functionality
- Cannot store any new content in knowledge base

### Suggested Fix
1. Provide users option to use paid OpenRouter key
2. Add local embedding model support (ollama embeddings)
3. Cache embeddings offline to avoid API dependency
4. Update config to require API key instead of relying on free tier
5. Add fallback chain: paid OpenRouter → local ollama → error with instructions

### Metadata
- Reproducible: yes
- Related Files:
 - config.py
 - src/storage/embeddings.py
 - .env file
- Tags: openrouter, model-access, embedding, api-failure
- See Also: ERR-20260311-001 (RateLimitError)

---

## [ERR-20260311-003] Python IndentationError in terminal

**Logged**: 2026-03-11T22:12:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Repeated IndentationError when writing multi-line Python scripts in terminal/code_execution_tool

### Error
```
IndentationError: expected an indented block after 'if' statement
```

### Context
- Occurs when using code_execution_tool with runtime python
- Multi-line scripts with if/try/with statements fail
- Same issue affected knowledge_base.py fix attempts (~20 failures)
- Pattern: Agent writes Python in terminal, indentation gets corrupted

### Recurrence
- First seen: 2026-03-11 (knowledge_base.py fix attempts)
- Count: 20+ times
- Also occurred when fetching YouTube transcripts (3+ times)

### Suggested Fix
Use file-based approach: write script to file with cat/heredoc, then execute
Avoid multi-line Python in terminal - use single commands or file execution

### Metadata
- Reproducible: yes
- Related Files: src/knowledge_base.py
- See Also: ERR-20260311-001 (API rate limits)

---
