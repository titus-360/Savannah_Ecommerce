#!/usr/bin/env python3
import os
import re
from pathlib import Path

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    # Ensure newline at end of file
    if not content.endswith('\n'):
        content += '\n'

    # Fix blank lines containing whitespace
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)

    # Fix comment spacing (at least two spaces before inline comment)
    content = re.sub(r'([^ ])  #', r'\1  #', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Get all Python files in the project
    python_files = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    # Fix each file
    for file_path in python_files:
        print(f"Fixing {file_path}...")
        fix_file(file_path)

if __name__ == '__main__':
    main()
