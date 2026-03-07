#!/usr/bin/env python3
"""Fix Unicode issues in aggressive burn script"""

import re

def fix_unicode_issues():
    """Remove problematic Unicode characters"""

    with open('aggressive_burn_subprocess.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace fire emojis and other problematic Unicode
    content = content.replace('🔥', 'FIRE')
    content = content.replace('💾', 'SAVE')
    content = content.replace('🎯', 'TARGET')
    content = content.replace('⭐', 'STAR')
    content = content.replace('❌', 'X')
    content = content.replace('🚀', 'ROCKET')

    with open('aggressive_burn_subprocess.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Unicode issues fixed")

if __name__ == "__main__":
    fix_unicode_issues()
