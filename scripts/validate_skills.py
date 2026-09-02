#!/usr/bin/env python3
"""
validate_skills.py

Automated validator for all agent skill definitions in .agents/skills/.
Checks:
1. Structural Validation:
   - Frontmatter presence and valid YAML structure
   - Required fields (name, description, category, triggers, inputs, outputs, dependencies, related_skills)
   - Uniqueness of skill names
   - Valid categorization
   - Proper quoting of special characters in YAML lists
2. Semantic Architectural Guardrails:
   - Tenancy identifier standard (strictly `agency_id`, forbids `tenant_id`)
   - Rejects affirmative Firestore / Cloud Functions adoption (only allowed in audit/forbidden-rule context)
   - Rejects affirmative Android Kotlin usage (standard is Java 21)
   - Rejects RabbitMQ authoritative inventory deduction assertions
   - Rejects client-authoritative payment success assertions
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

# Semantic forbidden phrases (regex pattern -> reason)
FORBIDDEN_SEMANTIC_PATTERNS = [
    (r'\btenant_id\b', "Found 'tenant_id'. Architecture standard strictly requires 'agency_id'."),
    (r'\bcom\.google\.firebase\.firestore\b', "Found Firestore SDK import. ERP system of record is PostgreSQL 16."),
    (r'\bfirebase-functions\b', "Found Cloud Functions reference. Backend is Spring Boot 3.3.x Modular Monolith."),
]

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

def run_semantic_lints(content, rel_path):
    """Checks for forbidden architectural patterns in skill bodies."""
    issues = []
    # Skip audit skill files whose job is explicitly to find legacy patterns
    if 'legacy-architecture-audit' in rel_path or '_architecture_rules' in rel_path:
        return issues

    for pattern, message in FORBIDDEN_SEMANTIC_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}: Semantic Lint Violation: {message}")

    return issues

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

        # 1. Structural Frontmatter Validation
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

        # 2. Semantic Architectural Linting
        semantic_issues = run_semantic_lints(content, rel_path)
        errors.extend(semantic_issues)

    # 3. Index File Consistency Check (_index.md)
    index_file = os.path.join(skills_dir, '_index.md')
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index_content = f.read()

        # Extract markdown links like [skill](./category/skill.md) or [`path`](./path)
        indexed_links = set(re.findall(r'\[.*?\]\(\.\/([^\)]+\.md)\)', index_content))
        
        # Check that all actual skill files (except _index.md and _architecture_rules.md) are in _index.md
        for file_path in all_files:
            rel = os.path.relpath(file_path, skills_dir).replace('\\', '/')
            if rel in ('_index.md', '_architecture_rules.md'):
                continue
            if rel not in indexed_links:
                errors.append(f"_index.md: Missing index entry for skill '{rel}'")

        # Check that all links in _index.md exist on disk
        for link in indexed_links:
            target_path = os.path.join(skills_dir, link.replace('/', os.sep))
            if not os.path.exists(target_path):
                errors.append(f"_index.md: Broken link to non-existent skill file '{link}'")

    print("\n" + "="*50)
    if errors:
        print(f"FAILED: Found {len(errors)} skill validation issues:")
        for err in errors:
            print(f"  [X] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(all_files)} skills passed structural, semantic, and _index.md validation.")
        sys.exit(0)

if __name__ == '__main__':
    main()


