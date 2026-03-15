#!/bin/bash
# Quick file analysis script
# Usage: analyze.sh <file>

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: analyze.sh <file>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

echo "=== File Analysis: $FILE ==="
echo ""
echo "Type: $(file -b "$FILE" 2>/dev/null || echo 'unknown')"
echo "Size: $(du -h "$FILE" 2>/dev/null | cut -f1)"
echo "Lines: $(wc -l < "$FILE" 2>/dev/null | tr -d ' ')"
echo "Words: $(wc -w < "$FILE" 2>/dev/null | tr -d ' ')"
echo "Bytes: $(wc -c < "$FILE" 2>/dev/null | tr -d ' ')"
echo ""
echo "=== First 10 lines ==="
head -10 "$FILE" 2>/dev/null
echo ""
echo "=== Last 5 lines ==="
tail -5 "$FILE" 2>/dev/null
echo ""
echo "=== End of analysis ==="
