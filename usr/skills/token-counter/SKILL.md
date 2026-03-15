---
name: "token-counter"
description: "Monitor, analyze and optimize token usage across Agent Zero operations. Use when tracking costs, analyzing efficiency, or optimizing context windows."
version: "1.0.0"
author: "Frugal Orchestrator"
tags: ["tokens", "optimization", "cost", "monitoring", "efficiency"]
trigger_patterns:
  - "token count"
  - "token usage"
  - "how many tokens"
  - "token efficiency"
  - "optimize tokens"
  - "cost analysis"
  - "context window"
---

# Token Counter

## When to Use

Activate when user needs to:
- Monitor token consumption
- Analyze cost efficiency
- Optimize context window usage
- Compare token usage between approaches
- Track token usage over time

## Quick Commands

### Count Tokens in Text
```bash
# Using wc (approximate: 1 token ≈ 4 chars)
echo "text here" | wc -c | awk '{print int($1/4)}'

# More accurate with Python
python3 -c "import sys; text=sys.stdin.read(); print(f'Chars: {len(text)}, Est tokens: {len(text)//4}')"
```

### Check Conversation Size
```bash
# Check current conversation file size
ls -lh /a0/tmp/chats/*/messages.json 2>/dev/null | tail -1
```

## Token Efficiency Rules

| Technique | Token Savings | When to Use |
|-----------|--------------|-------------|
| `§§include()` | 50-90% | Repeating tool outputs |
| Tables vs lists | 30-40% | Structured data |
| Abbreviated paths | 10-20% | File references |
| Skip pleasantries | 5-15% | Every response |
| Bullet points | 20-30% | vs paragraphs |

## Analysis Process

### Step 1: Measure Current Usage
- Check message history size
- Identify repetitive content
- Flag full rewrites vs includes

### Step 2: Identify Waste
- Repeated tool outputs rewritten
- Overly verbose explanations
- Unnecessary formatting
- Redundant context

### Step 3: Apply Optimizations
- Replace rewrites with `§§include()`
- Use tables for structured data
- Remove filler words
- Prefer concise formats

### Step 4: Verify Savings
- Compare before/after token estimates
- Check response quality maintained
- Document patterns for future use

## Token Estimation Formula

```python
def estimate_tokens(text):
    """Rough token estimation"""
    chars = len(text)
    words = len(text.split())
    # GPT-style: ~4 chars per token, or ~0.75 words per token
    est_by_chars = chars // 4
    est_by_words = int(words * 0.75)
    return (est_by_chars + est_by_words) // 2
```

## Anti-Patterns to Flag

❌ **Full Rewrites**
```json
{"text": "Tool output was: Lorem ipsum dolor sit amet... [1000 chars]"}
```

✅ **Smart Include**
```json
{"text": "See tool result: §§include(/a0/tmp/.../messages/10.txt)"}
```

❌ **Verbose Lists**
- Item one with long description
- Item two with long description
- Item three with long description

✅ **Compact Tables**
| Item | Status | Note |
|------|--------|------|
| One | Done | Brief |
| Two | Pending | Brief |

## Cost Reference

| Model | Input/1M | Output/1M | Context |
|-------|----------|-----------|---------|
| GPT-4 | $30 | $60 | 128K |
| Claude 3.5 | $3 | $15 | 200K |
| Kimi K2.5 | $2.4 | $9.6 | 256K |
| Local/OLL | $0 | $0 | varies |

## Output Format

Always present token analysis as:

```
## Token Analysis: [Task Name]

**Estimated Usage**: ~X tokens
**Efficiency Rating**: [Excellent/Good/Poor]

**Optimizations Applied**:
1. [technique] - saved ~X tokens
2. [technique] - saved ~X tokens

**Recommendation**: [specific advice]
```
