---
name: "file-analyzer"
description: "Analyze file contents efficiently without loading entirely into context. Use when examining large files, extracting patterns, or generating file statistics."
version: "1.0.0"
author: "Frugal Orchestrator"
tags: ["files", "analysis", "stats", "patterns", "streaming", "efficiency"]
trigger_patterns:
  - "analyze file"
  - "file stats"
  - "extract from"
  - "search in file"
  - "file contents"
---

# File Analyzer

## When to Use

Activate when:
- Examining large files without full load
- Extracting specific patterns or data
- Generating file statistics
- Sampling content for overview
- Analyzing structure without parsing fully

## Core Principle

**Stream, don't load.**

```bash
# ❌ AI-expensive: Reading entire file into context
content = open('huge.log').read()  # Token bomb!

# ✅ System-efficient: Streaming analysis
grep "ERROR" huge.log | head -20  # Just errors, limited
```

## Analysis Commands

### Quick Stats
```bash
# Line/word/byte count
wc -lwc file.txt

# File type
file file.txt

# Size
du -sh file.txt
ls -lh file.txt
```

### Content Sampling
```bash
# Preview structure
head -n 20 file.txt      # First 20 lines
tail -n 20 file.txt      # Last 20 lines
shuf -n 20 file.txt      # Random 20 lines

# Sample from middle
sed -n '100,120p' file.txt
awk 'NR>=100 && NR<=120' file.txt
```

### Pattern Extraction
```bash
# Count matches
grep -c "pattern" file.txt

# Extract with context
grep -A 2 -B 2 "pattern" file.txt | head -50

# Unique values
cut -d',' -f3 file.csv | sort | uniq -c | sort -rn | head -20
```

### Structured Data
```bash
# CSV/TSV columns
head -1 file.csv | tr ',' '\n' | nl  # List columns
awk -F',' '{print $1, $3}' file.csv | head -20  # Extract columns

# JSON
jq 'keys' file.json        # Top-level keys
jq '.[] | .name' file.json | head -20  # Extract field
```

## Analysis Scripts

Location: `/a0/usr/skills/file-analyzer/scripts/`

### analyze.sh
```bash
#!/bin/bash
# Quick file analysis
file="$1"
echo "=== Analysis: $file ==="
echo "Type: $(file -b "$file")"
echo "Size: $(du -h "$file" | cut -f1)"
echo "Lines: $(wc -l < "$file")"
echo "=== Sample (first 10 lines) ==="
head -10 "$file"
echo "=== Sample (last 5 lines) ==="
tail -5 "$file"
```

### sample.py
```python
#!/usr/bin/env python3
"""Smart file sampler for large files."""
import sys
from pathlib import Path

def sample_file(filepath, n_samples=10):
    """Get representative sample from file."""
    path = Path(filepath)
    total_lines = sum(1 for _ in open(filepath))
    
    # Sample from start, middle, end
    samples = []
    positions = [0, total_lines//2, total_lines-n_samples]
    
    with open(filepath) as f:
        for pos in positions:
            f.seek(0)
            for i, line in enumerate(f):
                if i >= pos and i < pos + n_samples//3:
                    samples.append((i, line.strip()))
                if i >= pos + n_samples//3:
                    break
    
    return total_lines, samples

if __name__ == "__main__":
    filepath = sys.argv[1]
    total, samples = sample_file(filepath)
    print(f"File: {filepath}")
    print(f"Total lines: {total}")
    print("Samples:")
    for line_num, content in samples:
        print(f"  Line {line_num}: {content[:80]}...")
```

## Report Template

When analyzing files, output:

```markdown
## File Analysis: `/path/to/file.ext`

**Metadata**:
| Property | Value |
|----------|-------|
| Size | X MB |
| Lines | Y |
| Type | Z |

**Sample** [first 10 lines + representative middle section]:
```
[line 1]
[line 2]
...
```

**Key Findings**:
- Pattern A: found X times
- Pattern B: found Y times
- Structure: [describe if structured]
- Sample: [first/last lines or representative snippet]

**Key Metrics**:
| Metric | Value |
|--------|-------|
| Total lines | X |
| Unique entries | Y |
| Pattern matches | Z |

**Recommendations**: [how to process efficiently]
```

## Efficiency Tips

- Never `cat` huge files - use `head`, `tail`, `shuf`
- Sample instead of scanning when possible
- Use `grep -m` to limit matches
- Stream with `| head` to limit output
- For binary: `strings` then analyze text output

## Anti-Patterns

❌ **Full File Load**
```python
content = open('huge.txt').read()  # Memory bomb!
```

✅ **Streaming/Iterating**
```python
for line in open('huge.txt'):
    process(line)
```

❌ **Regex on Binary**
```python
re.findall(pattern, binary_data)  # Bad!
```

✅ **Strings First**
```bash
strings binary | grep pattern
```
