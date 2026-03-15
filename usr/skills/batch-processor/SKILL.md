---
name: "batch-processor"
description: "Process multiple files or tasks efficiently in batch mode. Use when handling repetitive operations on collections of files, data batches, or parallel task execution."
version: "1.0.0"
author: "Frugal Orchestrator"
tags: ["batch", "parallel", "files", "automation", "efficiency", "bulk"]
trigger_patterns:
  - "batch process"
  - "process all files"
  - "bulk operation"
  - "parallel execution"
  - "process multiple"
---

# Batch Processor

## When to Use

Activate when:
- Processing multiple files with same operation
- Running repetitive tasks in bulk
- Need parallel execution for speed
- Transforming data at scale
- Batch converting/formatting files

## Core Philosophy

**Process once, apply everywhere.**

Replace AI loop with system-level batch operations:
```bash
# ❌ AI-expensive: Processing each file individually in a loop
for file in *.txt; do
    ai_process "$file"  # Token burn!done

# ✅ System-efficient: Single command, all files
sed -i 's/old/new/g' *.txt
```

## Batch Patterns

### Pattern 1: File Collection

```bash
# Find files matching criteria
find /data -name "*.log" -mtime +30 -type f

# Collect into batch
files=($(find /data -name "*.log" -mtime +30))
echo "Found ${#files[@]} files to process"
```

### Pattern 2: Parallel Processing

```bash
# GNU Parallel - process N jobs at once
parallel -j 4 'process_file {}' ::: *.txt

# xargs parallel
ls *.txt | xargs -P 4 -I {} process_file {}
```

### Pattern 3: Batch Transformation

```bash
# In-place edit all files
sed -i 's/foo/bar/g' *.txt

# Bulk rename (rename command)
rename 's/\.txt$/.csv/' *.txt

# Batch convert images
magick mogrify -format jpg *.png
```

### Pattern 4: Chunked Processing

```bash
# Process in chunks of 1000 lines
split -l 1000 hugefile.txt chunk_
for chunk in chunk_*; do
    process "$chunk"
done
```

## Efficiency Rules

| Rule | Implementation | Savings |
|------|---------------|---------|
| Collect First | `find`/`ls` then process | Avoids repeated scans |
| Parallelize | `parallel`/`xargs -P` | Nx speedup |
| In-Place | `sed -i`, `mogrify` | No temp files |
| Stream | `| process` vs `> file; process file` | Memory savings |

## Scripts

Location: `/a0/usr/skills/batch-processor/scripts/`

### batch_convert.py
```python
#!/usr/bin/env python3
"""Batch convert files with parallel processing."""
import sys
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def convert_file(filepath, output_ext, command_template):
    """Convert a single file."""
    path = Path(filepath)
    output = path.with_suffix(output_ext)
    cmd = command_template.format(input=filepath, output=output)
    subprocess.run(cmd, shell=True, check=True)
    return output

if __name__ == "__main__":
    # Example: batch_convert.py *.pdf .txt "pdftotext {input} {output}"
    pass
```

## Example Workflows

### Workflow: Batch Resize Images
```bash
# Create output dir
mkdir -p /tmp/resized

# Resize all images in parallel
parallel 'convert {} -resize 50% /tmp/resized/{/}' ::: *.jpg

# Report
ls /tmp/resized/ | wc -l
echo "Resized $(ls *.jpg | wc -l) images"
```

### Workflow: Process Log Files
```bash
# Find all logs older than 7 days
find /var/log -name "*.log" -mtime +7 > /tmp/old_logs.txt

# Compress in parallel
cat /tmp/old_logs.txt | parallel 'gzip {}'

# Verify savings
du -sh /var/log/*.gz | awk '{sum+=$1} END {print "Total:", sum}'
```

## Anti-Patterns

❌ **Sequential AI Processing**
```python
for file in files:
    result = ai_analyze(file)  # Token burn per file!
```

✅ **System Batch + AI Summary**
```bash
# Extract patterns first
grep -h "ERROR" *.log > /tmp/errors.txt

# Then AI analyze condensed output
ai_analyze /tmp/errors.txt  # One call, not N
```

## Safety Features

```bash
# Dry run first
echo "Will process:" && ls *.txt | head -5

# Backup before batch edit
cp -r /data /data.bak.$(date +%s)

# Verify with sample
head -1 *.txt | grep "pattern"  # Test on first lines
```
