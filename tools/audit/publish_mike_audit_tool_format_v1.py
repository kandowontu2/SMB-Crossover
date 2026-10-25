"""Remove tool-only trailing whitespace, retaining exact qualified originals.

The deployment sources and original proof/tool bindings are never rewritten.
Python AST equality verifies that published helpers execute the same code.
"""
from pathlib import Path
import ast
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/mike-native-current5ec-v1')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out = D / 'publication-format-v3'
    out.mkdir(exist_ok=False)
    rows = {}
    for name in ['mike_native_music_dispatch_cpu.py', 'mike_native_music_probe.py']:
        p = ROOT / 'tools/audit' / name
        raw = (D / 'ready-v1/tools' / name).read_bytes()
        text = raw.decode('utf-8')
        # Universal-newline interpretation already used by Python, followed
        # by removal of nonsemantic whitespace on physical line ends.
        normalized = text.replace('\r\n', '\n').replace('\r', '\n')
        clean = '\n'.join(line.rstrip(' \t') for line in normalized.split('\n')).rstrip('\n') + '\n'
        assert ast.dump(ast.parse(text)) == ast.dump(ast.parse(clean)), name
        (out / name).write_bytes(raw)
        p.write_bytes(clean.encode('utf-8'))
        rows[name] = dict(qualified_sha256=sha(out / name), published_sha256=sha(p),
                          Python_AST_identical=True)
    proof = dict(passed=True, source_or_ROM_changes=False, tools=rows,
                 original_receipts_and_ready_packet_unchanged=True,
                 retained_preflight='v1 stopped before mutation because collapsing double-CR also changed the module docstring. v2 preserved the docstring but retained an extra blank EOF line. v3 preserves universal-newline semantics and removes only trailing EOF whitespace. Both earlier outputs remain external.',
                 reason='Double-CR line endings and one trailing space flagged by staged diff check; published Python syntax trees remain identical.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    checkpoint = ROOT / 'docs/qa/checkpoints/2026-10-25/mike-native-9e0e'
    shutil.copy2(out / 'proof.json', checkpoint / 'published-tool-format.json')
    manifest = checkpoint / 'manifest.json'
    shutil.copy2(manifest, out / 'pre-publication-manifest.json')
    obj = json.loads(manifest.read_text())
    for name in rows:
        obj['tools']['tools/audit/' + name] = sha(ROOT / 'tools/audit' / name)
    obj['tools']['tools/audit/publish_mike_audit_tool_format_v1.py'] = sha(Path(__file__))
    obj['files']['published-tool-format.json'] = sha(checkpoint / 'published-tool-format.json')
    obj['original_qualified_tool_bytes_retained'] = str(out)
    manifest.write_text(json.dumps(obj, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
