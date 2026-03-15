---
name: "a0-token-optimizer"
description: "Optimize Agent Zero token usage and API costs through smart context management, model routing, and configuration tuning. Ported from openclaw-token-optimizer."
version: "1.0.0"
author: "Agent Zero (Ported)"
tags: ["optimization", "tokens", "cost", "performance"]
trigger_patterns:
  - "optimize tokens"
  - "reduce costs"
  - "token efficiency"
  - "model routing"
---

# Agent Zero Token Optimizer

Comprehensive toolkit for reducing token usage and API costs in Agent Zero. Features smart model routing, context optimization, and configuration tuning for /a0/usr/settings.json.

## Quick Start

1. **Optimize Prompt Files (BIGGEST WIN!):**
   Add the "Token Efficiency Rules" to /a0/prompts/agent.system.behaviour.md to enforce concise behavior.

2. **Tune System Settings:**
   Update /a0/usr/settings.json with aggressive compaction and response caps:
   - chat_model_ctx_length: 50000
   - chat_model_ctx_history: 0.5
   - max_tokens: 2048 (in chat_model_kwargs)

3. **Smart Model Routing:**
   Use Haiku/Flash for routine tasks and Sonnet/Pro for complex ones.

## Core Capabilities

### 1. Context Optimization
Only load files you actually need. Agent Zero already uses workdir_max_lines and memory_recall_history_len to keep context lean.

**Integration:**
Set workdir_max_lines: 100 and memory_recall_history_len: 5000 in /a0/usr/settings.json.

### 2. Smart Model Routing
Automatically classify tasks and route to appropriate model tiers. 

**Guidelines:**
- **Casual Chat/Acknowledgment**: Use Haiku / Gemini Flash.
- **Standard Tasks/Coding**: Use Sonnet / Gemini Pro.
- **Complex Reasoning**: Use Opus / Gemini Ultra.

### 3. Token Tracking
Monitor usage in /a0/usr/settings.json (if logging is enabled) or via model provider dashboards.

## Configuration Patches (for /a0/usr/settings.json)

### Aggressive Compaction
json
{
  "chat_model_ctx_history": 0.5
}

*Triggers summarization when 50% of context is full.*

### Response Capping
json
{
  "chat_model_kwargs": {
    "max_tokens": 2048,
    "temperature": 0.2
  }
}


## Procedures

### Apply Optimizations
Use the scripts/apply_a0_optimizations.py script to safely update your configuration.

### Verify Status
Check /a0/usr/settings.json to ensure limits are active.
