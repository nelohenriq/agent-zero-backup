#!/usr/bin/env python3
"""Token Counter - Count tokens in text files for cost estimation."""

import sys
import os
import argparse

def estimate_tokens(text, model="gpt-4"):
    """Estimate tokens using rough approximation (4 chars ≈ 1 token)."""
    if model.startswith("gpt-4") or model.startswith("claude"):
        return len(text) // 4
    return len(text) // 4

def count_file_tokens(filepath, model="gpt-4"):
    """Count tokens in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        tokens = estimate_tokens(content, model)
        return {
            'file': filepath,
            'tokens': tokens,
            'chars': len(content),
            'lines': content.count('\n'),
            'status': 'ok'
        }
    except Exception as e:
        return {'file': filepath, 'tokens': 0, 'status': f'error: {e}'}

def main():
    parser = argparse.ArgumentParser(description='Count tokens in files')
    parser.add_argument('files', nargs='+', help='Files to analyze')
    parser.add_argument('--model', default='gpt-4', help='Model for estimation')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    results = []
    total_tokens = 0
    
    for pattern in args.files:
        if os.path.isdir(pattern):
            for root, _, files in os.walk(pattern):
                for f in files:
                    results.append(count_file_tokens(os.path.join(root, f), args.model))
        else:
            results.append(count_file_tokens(pattern, args.model))
    
    for r in results:
        total_tokens += r.get('tokens', 0)
        if args.json:
            import json
            print(json.dumps(r))
        else:
            if r['status'] == 'ok':
                print(f"{r['tokens']:>8} tokens | {r['chars']:>8} chars | {r['file']}")
            else:
                print(f"   error | {r['file']}: {r['status']}")
    
    print(f"\n{'='*60}")
    print(f"Total: {total_tokens:,} tokens (~${total_tokens/1000*0.01:.4f} at $0.01/1K)")

if __name__ == '__main__':
    main()
