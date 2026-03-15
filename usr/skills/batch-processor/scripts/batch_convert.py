#!/usr/bin/env python3
"""Batch convert files with parallel processing using xargs/parallel patterns."""

import sys
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_command(cmd, dry_run=False):
    """Execute or simulate a command."""
    if dry_run:
        print(f"[DRY-RUN] {cmd}")
        return True
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

def batch_convert(files, command_template, output_ext=None, parallel_jobs=4, dry_run=False):
    """Convert batch of files using command template.
    
    Args:
        files: List of file paths to process
        command_template: Template with {input} and {output} placeholders
        output_ext: Optional output extension
        parallel_jobs: Number of parallel workers
        dry_run: Show commands without executing
    """
    tasks = []
    for filepath in files:
        path = Path(filepath)
        if output_ext:
            output = path.with_suffix(output_ext)
        else:
            output = path.parent / f"{path.stem}_out{path.suffix}"
        
        cmd = command_template.format(input=filepath, output=output)
        tasks.append((filepath, output, cmd))
    
    success_count = 0
    with ThreadPoolExecutor(max_workers=parallel_jobs) as executor:
        futures = {executor.submit(run_command, cmd, dry_run): (fp, out) 
                   for fp, out, cmd in tasks}
        
        for future in as_completed(futures):
            filepath, output = futures[future]
            if future.result():
                print(f"✓ {filepath} → {output}")
                success_count += 1
            else:
                print(f"✗ Failed: {filepath}")
    
    print(f"\nProcessed: {success_count}/{len(files)} files")
    return success_count

def main():
    parser = argparse.ArgumentParser(description="Batch convert files with parallel processing")
    parser.add_argument("files", nargs="+", help="Files to process")
    parser.add_argument("-c", "--command", required=True, 
                        help="Command template with {input} and {output}")
    parser.add_argument("-e", "--ext", help="Output extension (e.g., .txt)")
    parser.add_argument("-j", "--jobs", type=int, default=4, 
                        help="Parallel jobs (default: 4)")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Show commands without executing")
    
    args = parser.parse_args()
    
    batch_convert(
        files=args.files,
        command_template=args.command,
        output_ext=args.ext,
        parallel_jobs=args.jobs,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()
