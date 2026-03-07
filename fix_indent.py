#!/usr/bin/env python3
"""
Safe indentation fix for aminoanalytica_pipeline.py
Fixes the misaligned return statement around line 138
"""

import os

def fix_pipeline_indentation():
    """Fix the indentation issue in the pipeline file"""

    pipeline_file = 'agents/aminoanalytica_pipeline.py'

    # Read the file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find and fix the problematic return statements
    fixed_count = 0
    for i, line in enumerate(lines):
        # Look for misaligned return statements
        if line.strip().startswith('return {'):
            # Check if it's incorrectly indented (should have 8 or 12 spaces depending on context)
            if not (line.startswith('        return {') or line.startswith('            return {')):
                print(f"Fixing line {i+1}: {repr(line.rstrip())}")
                # Fix the indentation - assume function level (8 spaces)
                lines[i] = '        return {\n'
                print(f"Fixed to: {repr(lines[i].rstrip())}")
                fixed_count += 1

    print(f"Fixed {fixed_count} return statements")

    # Write the corrected file
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"Pipeline indentation fixed successfully")

if __name__ == "__main__":
    fix_pipeline_indentation()
