#!/usr/bin/env python3
"""
Apply creation dates to references.md files.
Adds 생성일 column and wraps date fields in backtick code format.
Reads creation-dates.json (url -> YYYY-MM-DD mapping).
"""

import json
import re
import sys
import os

LIBRARY_BASE = os.path.expanduser("~/F1/f1-mas/library")
PRODUCTS = ["supermembers", "superchart", "cosduck", "commerce"]
DATES_FILE = "/tmp/creation-dates.json"


def load_dates():
    with open(DATES_FILE, 'r') as f:
        return json.load(f)


def process_references(filepath, dates):
    """Add 생성일 column to a references.md file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    changes = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Detect table header: | 문서명 | 링크 | 등록일 | 비고 |
        # or: | 문서명 | 소스 | 등록일 | 비고 |
        if stripped.startswith('|') and ('문서명' in stripped) and ('등록일' in stripped):
            # Check if 생성일 already exists
            if '생성일' in stripped:
                new_lines.append(line)
                i += 1
                continue

            # Add 생성일 column between 링크 and 등록일
            # Old: | 문서명 | 링크 | 등록일 | 비고 |
            # New: | 문서명 | 링크 | 생성일 | 등록일 | 비고 |
            cells = [c.strip() for c in stripped.split('|')]
            # cells: ['', '문서명', '링크/소스', '등록일', '비고', '']
            # Find 등록일 position
            reg_idx = None
            for ci, c in enumerate(cells):
                if '등록일' in c:
                    reg_idx = ci
                    break

            if reg_idx:
                cells.insert(reg_idx, '생성일')
                new_header = '| ' + ' | '.join(c for c in cells if c != '') + ' |'
                new_lines.append(new_header + '\n')

                # Next line is separator
                i += 1
                if i < len(lines) and lines[i].strip().startswith('|--'):
                    sep_cells = lines[i].strip().split('|')
                    # Add one more separator column
                    sep_parts = [c for c in sep_cells if c.strip()]
                    sep_parts.insert(reg_idx - 1, '--------')
                    new_sep = '|' + '|'.join(sep_parts) + '|'
                    new_lines.append(new_sep + '\n')
                    i += 1

                # Process data rows
                while i < len(lines) and lines[i].strip().startswith('|'):
                    row = lines[i].rstrip()
                    cells = [c.strip() for c in row.split('|')]
                    # cells: ['', 'title', 'link', 'date', 'desc', '']

                    # Extract URL from link cell to look up creation date
                    link_cell = cells[2] if len(cells) > 2 else ""
                    link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', link_cell)

                    created = ""
                    if link_match:
                        url = link_match.group(2)
                        created = dates.get(url, "")

                    # Wrap dates in code backticks
                    if created:
                        created_fmt = f'`{created}`'
                    else:
                        created_fmt = '—'

                    # Wrap existing 등록일 in code backticks
                    reg_date_cell = cells[reg_idx] if len(cells) > reg_idx else ""
                    if reg_date_cell and re.match(r'\d{4}-\d{2}-\d{2}', reg_date_cell):
                        reg_date_cell = f'`{reg_date_cell}`'

                    # Insert 생성일 before 등록일
                    if len(cells) > reg_idx:
                        cells[reg_idx] = reg_date_cell
                        cells.insert(reg_idx, created_fmt)

                    # Rebuild row
                    non_empty = [c for c in cells if c != '']
                    new_row = '| ' + ' | '.join(non_empty) + ' |'
                    new_lines.append(new_row + '\n')
                    changes += 1
                    i += 1

                continue
            else:
                new_lines.append(line)
                i += 1
                continue
        else:
            new_lines.append(line)
            i += 1

    return new_lines, changes


def main():
    dates = load_dates()
    print(f"Loaded {len(dates)} creation dates")

    for product in PRODUCTS:
        filepath = os.path.join(LIBRARY_BASE, product, "references.md")
        if not os.path.exists(filepath):
            print(f"  {product}: file not found")
            continue

        new_lines, changes = process_references(filepath, dates)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"  {product}: {changes} rows updated")


if __name__ == "__main__":
    main()
