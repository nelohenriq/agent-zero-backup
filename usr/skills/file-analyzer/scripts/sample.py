#!/usr/bin/env python3
"""Smart file sampler for large files. Streams instead of loading fully."""

import sys
import random
from pathlib import Path

def count_lines(filepath):
    """Count lines efficiently without loading file."""
    count = 0
    with open(filepath, 'rb') as f:
        for _ in f:
            count += 1
    return count

def sample_file(filepath, n_samples=10, method='distributed'):
    """Get representative sample from large file.
    
    Args:
        filepath: Path to file to sample
        n_samples: Number of samples to return
        method: 'distributed' (start/middle/end), 'random', or 'head'
    """
    path = Path(filepath)
    total_lines = count_lines(filepath)
    
    if total_lines <= n_samples:
        # File is small, return all
        with open(filepath) as f:
            return total_lines, [(i+1, line.rstrip()) 
                                  for i, line in enumerate(f)]
    
    samples = []
    
    if method == 'distributed':
        # Sample from start, middle, and end
        positions = [
            list(range(0, n_samples // 3)),
            list(range(total_lines // 2 - n_samples // 6, 
                      total_lines // 2 + n_samples // 6)),
            list(range(total_lines - n_samples // 3, total_lines))
        ]
        line_nums = [p for sublist in positions for p in sublist][:n_samples]
    elif method == 'random':
        line_nums = sorted(random.sample(range(total_lines), n_samples))
    else:  # head
        line_nums = list(range(n_samples))
    
    with open(filepath) as f:
        current_line = 0
        for target in sorted(line_nums):
            while current_line < target:
                next(f)
                current_line += 1
            samples.append((current_line + 1, next(f).rstrip()))
            current_line += 1
    
    return total_lines, samples

def analyze_structure(filepath):
    """Quick structural analysis without loading full file."""
    stats = {
        'total_lines': 0,
        'empty_lines': 0,
        'avg_line_length': 0,
        'has_header': False,
        'delimiter': None
    }
    
    total_length = 0
    first_lines = []
    
    with open(filepath) as f:
        for i, line in enumerate(f):
            stats['total_lines'] += 1
            if not line.strip():
                stats['empty_lines'] += 1
            total_length += len(line)
            if i < 5:
                first_lines.append(line)
    
    if stats['total_lines'] > 0:
        stats['avg_line_length'] = total_length / stats['total_lines']
    
    # Detect delimiter
    if first_lines:
        for delim in [',', '\t', '|', ';']:
            counts = [line.count(delim) for line in first_lines if line.strip()]
            if counts and min(counts) == max(counts) and max(counts) > 0:
                stats['delimiter'] = delim
                stats['columns'] = max(counts) + 1
                break
    
    return stats

def main():
    if len(sys.argv) < 2:
        print("Usage: sample.py <file> [samples] [method]")
        print("Methods: distributed (default), random, head")
        sys.exit(1)
    
    filepath = sys.argv[1]
    n_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    method = sys.argv[3] if len(sys.argv) > 3 else 'distributed'
    
    print(f"File: {filepath}")
    print("")
    
    # Quick stats
    stats = analyze_structure(filepath)
    print(f"Total lines: {stats['total_lines']:,}")
    print(f"Empty lines: {stats['empty_lines']:,}")
    print(f"Avg line length: {stats['avg_line_length']:.1f} chars")
    if stats['delimiter']:
        print(f"Detected delimiter: '{stats['delimiter']}' ({stats['columns']} columns)")
    print("")
    
    # Sampling
    total, samples = sample_file(filepath, n_samples, method)
    print(f"Samples ({method} method, {len(samples)} lines):")
    print("-" * 50)
    for line_num, content in samples:
        display = content[:80] + "..." if len(content) > 80 else content
        print(f"  L{line_num}: {display}")
    print("-" * 50)

if __name__ == "__main__":
    main()
