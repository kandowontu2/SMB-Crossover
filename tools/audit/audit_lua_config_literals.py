"""Inventory Python literals in frozen Lua evidence without editing receipts."""
from pathlib import Path
import argparse
import hashlib
import json
import re

LONG_OPEN = re.compile(r'\[(=*)\[')
IDENTIFIER = re.compile(r'[A-Za-z_][A-Za-z_0-9]*')


def bare_python_literals(text):
    """Skip Lua quoted strings, long strings and comments before tokenizing."""
    i, found = 0, []
    while i < len(text):
        comment = text.startswith('--', i)
        if comment:
            i += 2
        match = LONG_OPEN.match(text, i)
        if match:
            end = text.find(']' + match[1] + ']', i + len(match[0]))
            i = len(text) if end < 0 else end + len(match[1]) + 2
            continue
        if comment:
            end = text.find('\n', i)
            i = len(text) if end < 0 else end + 1
            continue
        if text[i] in ['"', "'"]:
            quote = text[i]
            i += 1
            while i < len(text):
                if text[i] == '\\':
                    i += 2
                elif text[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            continue
        match = IDENTIFIER.match(text, i)
        if match:
            if match[0] in ['True', 'False', 'None']:
                line = text.count('\n', 0, i) + 1
                start = text.rfind('\n', 0, i) + 1
                end = text.find('\n', i)
                context = text[start:end if end >= 0 else len(text)]
                column = i-start
                found.append(dict(literal=match[0], line=line, column=column+1,
                                  context=context[max(0, column-100):column+100]))
            i += len(match[0])
        else:
            i += 1
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    rows, hits = [], []
    for root in args.root:
        assert root.is_dir(), root
        for path in sorted(root.rglob('*.lua')):
            if '__pycache__' in path.parts:
                continue
            raw = path.read_bytes()
            bad = bare_python_literals(raw.decode('utf-8-sig'))
            row = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), bare_python_literals=bad)
            rows.append(row)
            if bad:
                hits.append(row)
    result = dict(audit_complete=True, game_ROM_changed=False, original_receipts_edited=False,
                  scanned_files=len(rows), files_with_bare_python_literals=len(hits),
                  roots=[str(p) for p in args.root], hits=hits,
                  scope='Lexical inventory only. Bare Python True/False/None are Lua globals and normally nil; each affected control/claim needs semantic review. Strings and comments excluded. No native mode or gameplay pass inferred.')
    (args.output / 'files.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    (args.output / 'proof.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'hits'}, indent=2))


if __name__ == '__main__':
    main()
