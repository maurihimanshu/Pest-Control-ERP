#!/usr/bin/env python3
"""
validate_skills.py

Automated validator for all agent skill definitions in .agents/skills/.
Checks:
- Frontmatter presence and valid YAML structure
- Required fields (name, description, category, triggers, inputs, outputs, dependencies, related_skills)
- Uniqueness of skill names
- Valid categorization
- Proper quoting of special characters in YAML lists
"""

import os
import sys
import re

VALID_CATEGORIES = {
    'architecture', 'backend', 'database', 'domain', 'security',
    'android', 'admin', 'api', 'messaging', 'caching', 'testing',
    'devops', 'observability', 'documentation', 'git', 'workflows'
}

REQUIRED_KEYS = {
    'name', 'description', 'category', 'triggers', 'inputs',
    'outputs', 'dependencies', 'related_skills'
}

def parse_simple_yaml(yaml_text, file_path):
    lines = yaml_text.splitlines()
    data = {}
    current_key = None
    list_accumulator = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Check for unquoted reserved characters at start of list item
        if re.search(r'^\s*-\s*@', line):
            raise ValueError(f"Line {line_num}: Unquoted '@' reserved character at start of value: {line}")

        if re.search(r'^\s*-\s*[`*&!%#]', line):
            raise ValueError(f"Line {line_num}: Unquoted special character at start of list item: {line}")

        # Key-value match
        kv_match = re.match(r'^([a-zA-Z0-9_-]+)\s*:\s*(.*)$', line)
        if kv_match and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('-'):
            if current_key and list_accumulator is not None:
                data[current_key] = list_accumulator
            current_key = kv_match.group(1)
            val = kv_match.group(2).strip()
            if val == '[]':
                data[current_key] = []
                list_accumulator = None
            elif val == '':
                list_accumulator = []
            else:
                # remove optional quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                data[current_key] = val
                list_accumulator = None
        elif line.strip().startswith('-') and current_key and list_accumulator is not None:
            item = re.sub(r'^\s*-\s*', '', line).strip()
            if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                item = item[1:-1]
            list_accumulator.append(item)

    if current_key and list_accumulator is not None:
        data[current_key] = list_accumulator

    return data

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(repo_root, '.agents', 'skills')

    if not os.path.exists(skills_dir):
        print(f"Error: Skills directory not found at {skills_dir}")
        sys.exit(1)

    all_files = []
    for root, _, files in os.walk(skills_dir):
        for f in files:
            if f.endswith('.md'):
                all_files.append(os.path.join(root, f))

    print(f"Validating {len(all_files)} markdown files in {skills_dir}...")

    errors = []
    skill_names = set()

    for file_path in sorted(all_files):
        rel_path = os.path.relpath(file_path, skills_dir)
        with open(file_path, 'r', encoding='utf-8') as fh:
            content = fh.read()

        if not content.startswith('---'):
            errors.append(f"{rel_path}: Missing frontmatter start delimiter (---)")
            continue

        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append(f"{rel_path}: Incomplete frontmatter block")
            continue

        yaml_content = parts[1]
        try:
            frontmatter = parse_simple_yaml(yaml_content, rel_path)
        except Exception as e:
            errors.append(f"{rel_path}: YAML parsing error: {e}")
            continue

        # Check required keys
        missing_keys = REQUIRED_KEYS - set(frontmatter.keys())
        if missing_keys:
            errors.append(f"{rel_path}: Missing required frontmatter keys: {missing_keys}")

        # Check name uniqueness
        name = frontmatter.get('name')
        if not name:
            errors.append(f"{rel_path}: 'name' field is empty or missing")
        elif name in skill_names:
            errors.append(f"{rel_path}: Duplicate skill name '{name}'")
        else:
            skill_names.add(name)

        # Check category validity
        category = frontmatter.get('category')
        if category and category not in VALID_CATEGORIES:
            errors.append(f"{rel_path}: Invalid category '{category}'. Allowed: {VALID_CATEGORIES}")

    print("\n" + "="*50)
    if errors:
        print(f"FAILED: Found {len(errors)} skill validation issues:")
        for err in errors:
            print(f"  [X] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(all_files)} skills passed validation (unique names, valid frontmatters, valid categories).")
        sys.exit(0)

if __name__ == '__main__':
    main()
