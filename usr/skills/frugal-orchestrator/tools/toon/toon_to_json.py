#!/usr/bin/env python3
"""
TOON to JSON converter for Frugal Orchestrator.
Parses TOON format back to standard JSON.
"""
import json
import sys
import re

def parse_toon(content):
    """Parse TOON content and return Python object."""
    lines = content.split('\n')
    root = {}
    current = root
    stack = [(root, -1, None)]  # (object, indent_level, key)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        
        # Calculate indent level
        indent = len(line) - len(line.lstrip())
        content = line.strip()
        
        # Check for array table header: key[N]{fields}:
        table_match = re.match(r'^(\w+)\[(\d+)\]\{([^}]+)\}:$', content)
        if table_match:
            key = table_match.group(1)
            count = int(table_match.group(2))
            fields = [f.strip() for f in table_match.group(3).split(',')]
            
            arr = []
            i += 1
            for _ in range(count):
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i >= len(lines):
                    break
                row = lines[i].strip()
                values = [v.strip() for v in row.split(',')]
                item = {}
                for j, field in enumerate(fields):
                    if j < len(values):
                        item[field] = parse_value(values[j])
                    else:
                        item[field] = ""
                arr.append(item)
                i += 1
            
            _set_in_structure(stack, indent, key, arr)
            continue
        
        # Check for key: value
        if ':' in content:
            key, val = content.split(':', 1)
            key = key.strip()
            val = val.strip()
            
            if val:
                _set_in_structure(stack, indent, key, parse_value(val))
            else:
                # Empty value - likely a parent
                new_obj = {}
                _set_in_structure(stack, indent, key, new_obj)
                stack.append((new_obj, indent, key))
        
        i += 1
    
    return root

def parse_value(val):
    """Parse a TOON value to Python type."""
    # Check for array marker like "[3]"
    if re.match(r'^\[\d+\]$', val):
        return []
    
    # Try int
    if re.match(r'^-?\d+$', val):
        return int(val)
    
    # Try float
    if re.match(r'^-?\d+\.\d+$', val):
        return float(val)
    
    # Try bool
    if val.lower() == 'true':
        return True
    if val.lower() == 'false':
        return False
    if val.lower() == 'null' or val.lower() == 'none':
        return None
    
    return val

def _set_in_structure(stack, indent, key, value):
    """Set a value in the correct nested structure."""
    # Pop stack until we find the right level
    while len(stack) > 1 and stack[-1][1] >= indent:
        stack.pop()
    
    current = stack[-1][0]
    if isinstance(current, dict):
        current[key] = value
    elif isinstance(current, list):
        current.append(value)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python toon_to_json.py <file.toon>", file=sys.stderr)
        print("  or: cat file.toon | python toon_to_json.py -", file=sys.stderr)
        sys.exit(1)
    
    if sys.argv[1] == '-':
        content = sys.stdin.read()
    else:
        with open(sys.argv[1]) as f:
            content = f.read()
    
    data = parse_toon(content)
    print(json.dumps(data, indent=2))
