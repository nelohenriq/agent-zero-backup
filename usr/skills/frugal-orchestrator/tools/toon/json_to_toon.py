#!/usr/bin/env python3
"""
JSON to TOON converter for Frugal Orchestrator.
TOON: Token-Oriented Object Notation
~40% token reduction vs JSON.
"""
import json
import sys
import re

def json_to_toon(data, indent=0, is_array_item=False):
    """Convert Python object to TOON format."""
    spaces = "  " * indent
    
    if isinstance(data, dict):
        if not data:
            return "{}"
        lines = []
        for i, (key, value) in enumerate(data.items()):
            key_str = str(key)
            # Quote only if needed
            if re.search(r'[\s,]', key_str):
                key_str = f'"{key_str}"'
            val = json_to_toon(value, indent + 1)
            lines.append(f"{spaces}{key_str}: {val}" if indent == 0 else f"{spaces}{key_str}:{val}")
        return "\n".join(lines) if indent > 0 else "\n".join(lines)
    
    elif isinstance(data, list):
        if not data:
            return "[]"
        # Check if array of objects (tabular)
        if all(isinstance(x, dict) for x in data) and len(data) > 0:
            return format_tabular_array(data, indent)
        # Simple array
        items = [json_to_toon(x, indent + 1, True) for x in data]
        return f"[{len(data)}]:\n" + "\n".join(f"{spaces}  {x}" for x in items)
    
    elif isinstance(data, str):
        if re.search(r'[\n,]', data) or data.strip() != data:
            return f'"{data}"'
        return data
    else:
        return str(data).lower() if isinstance(data, bool) else str(data)

def format_tabular_array(arr, indent):
    """Format array of objects as TOON table."""
    spaces = "  " * indent
    if not arr:
        return "[]"
    
    # Get all unique keys
    keys = []
    for item in arr:
        for k in item.keys():
            if k not in keys:
                keys.append(k)
    
    lines = [f"[{len(arr)}]{{{','.join(keys)}}}:"]
    for item in arr:
        values = [str(item.get(k, "")) for k in keys]
        lines.append(f"{spaces}  {','.join(values)}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_to_toon.py <file.json>", file=sys.stderr)
        print("   or: cat file.json | python json_to_toon.py", file=sys.stderr)
        sys.exit(1)
    
    if sys.argv[1] == "-":
        data = json.load(sys.stdin)
    else:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    
    print(json_to_toon(data))
