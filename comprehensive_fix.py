#!/usr/bin/env python3
"""
Comprehensive fix for aminoanalytica_pipeline.py syntax issues
"""

import re

def fix_pipeline_syntax():
    """Fix all syntax issues in the pipeline file"""

    pipeline_file = 'agents/aminoanalytica_pipeline.py'

    # Read the file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the specific pattern where return { is followed by incorrect indentation
    # Look for return { followed by the closing brace issues
    lines = content.split('\n')

    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # If we find a return { line that's improperly formatted
        if line.strip().startswith('return {') and not line.strip() == 'return {}':
            # This should be a multi-line return statement
            # Ensure proper indentation
            indent = '        '  # Function level indentation
            fixed_lines.append(f'{indent}return {{')
            i += 1

            # Look for the closing brace and content between
            brace_count = 1
            while i < len(lines) and brace_count > 0:
                current_line = lines[i].rstrip()

                if current_line.strip() == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        fixed_lines.append(f'{indent}}}')
                    else:
                        fixed_lines.append(current_line)
                elif current_line.strip().startswith("'") or current_line.strip().startswith('"'):
                    # This is likely a dictionary key-value pair
                    fixed_lines.append(f'{indent}    {current_line.strip()}')
                elif current_line.strip() == '':
                    fixed_lines.append('')
                else:
                    # Preserve relative indentation
                    fixed_lines.append(current_line)

                i += 1
        else:
            fixed_lines.append(line)
            i += 1

    # Write the fixed content back
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))

    print("Pipeline syntax fixed comprehensively")

if __name__ == "__main__":
    fix_pipeline_syntax()
