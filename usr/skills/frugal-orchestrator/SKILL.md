---
name: "frugal-orchestrator"
description: "Token-efficient task orchestration system. Delegates work to specialized subordinates, prioritizes system-level solutions (Linux/Python) over AI inference. Central hub for frugal AI operations."
version: "0.5.0"
author: "Agent Zero Project"
tags: ["orchestration", "efficiency", "token-optimization", "delegation", "caching", "batch-processing"]
trigger_patterns:
  - "delegate"
  - "orchestrate"
  - "token efficient"
  - "batch process"
  - "system command"
  - "linux"
  - "frugal"
  - "subordinate"
  - "task routing"
allowed_tools: ["code_execution", "call_subordinate", "skills_tool", "memory_load", "memory_save"]
---

# Skill: Frugal Orchestrator

## Problem Statement
AI agents often waste tokens on tasks better solved by system tools (Linux commands, Python scripts). This creates unnecessary costs and slower execution.

**Solution**: Frugal Orchestrator v0.5.0 with intelligent task routing, caching layer, and specialized subordinate delegation.

**Result**: 90%+ token reduction while maintaining full functionality

## Core Capabilities

### Module 1: Auto-Router
Automatically detect task type and route optimally:
- System commands → Terminal (95% token reduction)
- Scripts → Python/Node.js execution
- Complex logic → AI delegation

### Module 2: Cache Manager
Token-efficient caching with TOON format:
- Memory persistence via FAISS + pickle
- TOON format for compressed storage
- Cross-session learning

### Module 3: Batch Processor
Process multiple files/tasks efficiently:
```bash
chmod +x delegate.sh && ./delegate.sh -t coder -f "task" -c "command"
```

### Module 4: Delegate Tool
Spawn specialized subordinates for domain-specific work.

## Usage Patterns

| Task Type | Delegate To | System Alternative |
|-----------|-------------|-------------------|
| File processing | coder | `awk`, `sed`, `jq` |
| Data fetching | researcher | `curl`, `wget` |
| Text parsing | coder | `grep`, `cut`, `tr` |
| Web scraping | browser_agent | `lynx -dump` |
| Security scan | hacker | `nmap`, `nikto` |

## Quick Commands

```bash
# Run standalone router
python auto_router.py -d /path/to/task

# Batch process files
python batch_processor.py --pattern "*.json"

# Convert metrics to TOON
python tools/toon/json_to_toon.py metrics.json metrics.toon
```

## Scripts Reference
- `auto_router.py` - Task detection and routing
- `cache_manager.py` - Token-efficient caching
- `batch_processor.py` - Batch operations
- `token_tracker.py` - Usage metrics
- `delegate.sh` - Subordinate delegation helper
- `tools/toon/` - TOON conversion utilities

## Key Principles
1. **System First** - Prefer Linux/Python over AI inference
2. **Delegate Specialized** - Spawn subordinates for specific domains
3. **Synthesize Briefly** - Consolidate outputs concisely
4. **Never Repeat** - Use §§include() for long content
