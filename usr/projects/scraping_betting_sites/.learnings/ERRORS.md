## [ERR-20260306-001] placard_scraper_fix

**Logged**: 2026-03-06T23:09:03
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
IndentationError occurred while fixing the Placard sports-betting API scraper.

### Error
```
IndentationError: unexpected indent
```

### Context
- Command/operation attempted: Fixing placard_sports_scraper.py
- Input: Previous code snippet with mixed indentation or incorrect block structure.
- Environment: Python 3.x in Kali Linux container.

### Suggested Fix
Ensure consistent 4-space indentation. Use a linter (flake8/black) before running. Verify list vs. dict structure in JSON parsing logic.

### Metadata
- Reproducible: yes
- Related Files: placard_sports_scraper.py, placard_api_scraper.py
- See Also: ERR-20250110-001 (if recurring)

---
## [ERR-20260306-002] placard_api_request

**Logged**: 2026-03-06T23:09:03
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
HTTP 405 Method Not Allowed error when scraping Placard API.

### Error
```
HTTP 405: Method Not Allowed
```

### Context
- Command/operation attempted: Sending HTTP request to Placard API endpoint.
- Input: Incorrect HTTP method (e.g., GET instead of POST) or missing headers.
- Environment: Python requests library.

### Suggested Fix
Verify the required HTTP method (POST/GET) and necessary headers (User-Agent, Authorization, Content-Type) for the specific Placard endpoint. Check API documentation or network traces.

### Metadata
- Reproducible: yes
- Related Files: placard_api_scraper.py
- See Also: ERR-20250110-001

---
## [ERR-20260307-RL1] RateLimitError - OpenAI 429

**Logged**: 2026-03-07T18:41:35Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Multiple 429 rate limit errors when calling subordinate agents

### Error
```
litellm.RateLimitError: Error code: 429 - {"status": 429, "title": "Too Many Requests"}
```

### Context
- Attempting to delegate Solverde scraping to hacker subordinate
- Rate limit hit on both call_subordinate attempts
- User granted autonomy to keep trying different approaches

### Suggested Fix
- Wait 30+ seconds between calls
- Consider implementing exponential backoff
- May need to reduce request frequency

### Metadata
- Reproducible: yes
- Related Files: call_subordinate tool
- See Also: Previous rate limit occurrences

---


## [ERR-20260307-001] solverde_url_404

**Logged**: 2026-03-07T23:03:06.014907
**Priority**: high
**Status**: pending
**Area**: scraping

### Summary
The direct URL `https://www.solverde.pt/pt-pt/apostas-desportivas` returns a 404 error.

### Error
```
Page loads 404: "Esta página não existe ou foi removida".
```

### Context
- Script: `solverde_final_attempt_v2.py`
- Attempted URL: `https://www.solverde.pt/pt-pt/apostas-desportivas`
- The site's navigation menu shows "APOSTAS DESPORTIVAS", but the direct link is broken.

### Suggested Fix
1. Navigate to the homepage (`https://www.solverde.pt`).
2. Accept cookies.
3. Locate the "APOSTAS DESPORTIVAS" link in the navigation menu.
4. Extract its `href` attribute to get the correct URL.
5. Navigate to the correct URL.

### Metadata
- Reproducible: yes
- Related Files: solverde_final_attempt_v2.py
- See Also: ERR-20250110-001 (if recurring)

---

## [ERR-20260311-003] betano_cloudflare_block

**Logged**: 2026-03-11T22:33:00Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Betano.pt has aggressive Cloudflare WAF protection blocking all automated requests

### Error
```
HTTP/2 403 Forbidden with Cloudflare challenge
All API endpoints (/robots.txt, /api, direct curl) return block
Binary/garbage response indicates compression + encrypted challenge
```

### Context
- Site: https://www.betano.pt
- Protection: Cloudflare with managed challenge
- Attempted: Standard curl, browser headers, compressed requests
- All blocked with 403 before reaching content

### Suggested Fix
Deploy browser automation with stealth plugins or advanced evasion techniques

### Metadata
- Reproducible: yes
- Related Files: N/A
- See Also: ERR-20260309-004 (429 rate limits on Solverde)

---

## [ERR-20260311-004] estorilsolcasinos_cloudflare_block

**Logged**: 2026-03-11T22:42:41Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Estoril Sol Casinos has strong Cloudflare WAF protection blocking automated access

### Error
```
HTTP/2 403
server: cloudflare
cf-ray: 9dae12e2d928a68a-ARN
set-cookie: __cf_bm=YjllU8Mug8xa5_FVym_eFJlxHyJUZYt8jbzz6kDbG0E-1773268961-1.0.1.1-WCYR9bKY4Dzvxzucjtp.i6QhhebHg1bHqVa3JP0KB4LGCS7t5w75uu19fO7wpYK1gOB62m_te5AQIsfaP3KuQzRfjdYlXnKeofitFNn0U9s
```

### Context
- Site: https://www.estorilsolcasinos.pt/pt/betting/home
- Protection: Cloudflare with managed challenge
- Location: ARN (Arlanda, Stockholm) - CDN edge

### Suggested Fix
Deploy browser automation with additional evasion techniques or analyze mobile API endpoints

### Metadata
- Reproducible: yes
- Related Files: N/A
- See Also: ERR-20260311-003 (Betano - same protection pattern)

---

## [ERR-20260311-005] estorilsolcasinos_browser_timeout

**Logged**: 2026-03-11T22:45:00Z
**Priority**: high
**Status**: pending
**Area**: frontend

### Summary
Playwright stealth browser timed out accessing Estoril Sol Casinos - indicates heavy anti-automation measures

### Error
```
Browser agent task timed out, no output provided
```

### Context
- Site: https://www.estorilsolcasinos.pt/pt/betting/home
- Method: Playwright with stealth configuration
- Timeout: 60s (configuration default)
- Previous: Cloudflare 403 from direct curl requests

### Suggested Fix
Increase wait time to 120s or attempt with different proxy/locale settings; consider mobile app API approach

### Metadata
- Reproducible: yes
- Related Files: N/A
- See Also: ERR-20260311-004 (same site - CF block)

---
