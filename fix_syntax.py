#!/usr/bin/env python3
"""
Fix syntax errors in aminoanalytica_pipeline.py caused by archival system addition
"""

def fix_pipeline_syntax():
    """Fix indentation and syntax errors in the pipeline file"""

    pipeline_file = 'agents/aminoanalytica_pipeline.py'

    print("Reading pipeline file...")
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the specific indentation error around _compile_final_metrics
    original = '''    def _compile_final_metrics(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """Compile final design quality metrics"""'''

    fixed = '''    def _compile_final_metrics(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compile final design quality metrics"""'''

    content = content.replace(original, fixed)

    # Fix any other method indentation issues
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # Fix method definitions and docstrings
        if 'def _compile_final_metrics' in line:
            fixed_lines.append(line)
            # Ensure next few lines are properly indented
            for j in range(i+1, min(i+20, len(lines))):
                next_line = lines[j]
                if next_line.strip() == '"""Compile final design quality metrics"""':
                    fixed_lines.append('        """Compile final design quality metrics"""')
                    break
                elif next_line.strip().startswith('boltz2_result'):
                    fixed_lines.append('        ' + next_line.strip())
                    break
                else:
                    fixed_lines.append(next_line)
            continue

        # Skip lines we already processed
        if i > 0 and any('_compile_final_metrics' in lines[k] for k in range(max(0, i-5), i)):
            if line.strip() == '"""Compile final design quality metrics"""':
                continue  # Already added with proper indentation
            elif line.strip().startswith('boltz2_result') and not line.startswith('        '):
                continue  # Will be fixed

        fixed_lines.append(line)

    # Reconstruct content
    content = '\n'.join(fixed_lines)

    # Additional fixes for common indentation issues
    content = content.replace(
        'boltz2_result = pipeline_results.get(',
        '        boltz2_result = pipeline_results.get('
    )
    content = content.replace(
        'pesto_result = pipeline_results.get(',
        '        pesto_result = pipeline_results.get('
    )
    content = content.replace(
        'iptm_score = boltz2_result.get(',
        '        iptm_score = boltz2_result.get('
    )
    content = content.replace(
        'interface_pae = boltz2_result.get(',
        '        interface_pae = boltz2_result.get('
    )
    content = content.replace(
        'hotspot_coverage = pesto_result.get(',
        '        hotspot_coverage = pesto_result.get('
    )
    content = content.replace(
        'binding_validated = pesto_result.get(',
        '        binding_validated = pesto_result.get('
    )
    content = content.replace(
        'overall_score = (',
        '        overall_score = ('
    )
    content = content.replace(
        'return {',
        '        return {'
    )

    print("Writing fixed content...")
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Syntax fix complete!")

def verify_syntax():
    """Verify the pipeline file has correct syntax"""

    try:
        import ast
        with open('agents/aminoanalytica_pipeline.py', 'r', encoding='utf-8') as f:
            content = f.read()

        ast.parse(content)
        print("SUCCESS: Pipeline syntax is valid!")
        return True

    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Fixing aminoanalytica_pipeline.py syntax...")
    fix_pipeline_syntax()

    print("\nVerifying syntax...")
    if verify_syntax():
        print("Pipeline file is ready for execution!")
    else:
        print("Manual syntax correction may be needed.")
