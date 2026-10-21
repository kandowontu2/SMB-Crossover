"""Reconstruct this task's QA document from its retained exact edit history.

Only writes recovery candidates and receipts. Does not execute historic scripts.
"""
from pathlib import Path
import ast, hashlib, json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda b: hashlib.sha256(b).hexdigest()

def apply_hunks(lines, body):
    groups = []
    for line in body.splitlines():
        if line.startswith('@@'):
            groups.append([])
        elif line == '*** End of File':
            continue
        else:
            if not groups:
                groups.append([])
            groups[-1].append(line)
    cursor = 0
    for group in groups:
        old = [x[1:] for x in group if x.startswith((' ', '-'))]
        new = [x[1:] for x in group if x.startswith((' ', '+'))]
        if any(not x or x[0] not in ' +-' for x in group):
            raise ValueError(('unexpected hunk', group))
        hits = [i for i in range(cursor, len(lines)-len(old)+1) if lines[i:i+len(old)] == old]
        if not hits:
            raise ValueError(('missing old hunk', old[:4], cursor))
        at = hits[0]
        lines[at:at+len(old)] = new
        cursor = at + len(new)
    return lines

def literal_append(path):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'QA':
                    constants['QA'] = ast.literal_eval(node.value)
    candidates = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != 'write_text' or not node.args:
            continue
        expr = node.args[0]
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add) and isinstance(expr.left, ast.Call) and isinstance(expr.left.func, ast.Attribute) and expr.left.func.attr == 'read_text':
            if isinstance(expr.right, ast.Name):
                candidates.append(constants[expr.right.id])
            else:
                candidates.append(ast.literal_eval(expr.right))
    assert len(candidates) == 1, (path, len(candidates))
    return candidates[0]

def main():
    patches = json.loads((V/'root49-QA-recovery-patches-fr.json').read_text(encoding='utf-8'))
    # The first attempted Add failed; the second successful Add is the retained file.
    lines = [x[1:] for x in patches[1]['body'].splitlines() if x.startswith('+')]
    # Successful FileChange receipts also include one dynamically constructed
    # patch missing from the initial literal-call extraction. Failed calls are
    # absent, as independently confirmed by their actual tool outputs.
    changes = json.loads((V/'root49-QA-recovery-filechanges-fs.json').read_text(encoding='utf-8'))
    history = []
    for p in changes[1:]:
        try:
            lines = apply_hunks(lines, p['diff'])
        except Exception as e:
            print('FAILED', p['line'], str(e))
            break
        b = ('\n'.join(lines)+'\n').encode('utf-8')
        history.append(dict(line=p['line'], bytes=len(b), LF_sha256=sha(b), CRLF_sha256=sha(b.replace(b'\n', b'\r\n'))))
    else:
        print('ALL_PATCHES_APPLIED', len(history))
    b = ('\n'.join(lines)+'\n').encode('utf-8')
    (V/'root49-QA-recovery-fr-candidate.md').write_bytes(b)
    (V/'root49-QA-recovery-fr-replay.json').write_text(json.dumps(history, indent=2)+'\n', encoding='utf-8')
    print('CANDIDATE', len(b), sha(b), 'CRLF', sha(b.replace(b'\n', b'\r\n')))
    assert sha(b) == '63f02dfb5a51a551321aaae4dadd4a7592d7aa9be50c2d5eb767316635a1cacd'
    stages = [('cg', 'a5b7fa166727fe5855c968f3b57eaf1b7e229b84e580816d620796062c34a1a1'),
              ('cv', '0cc1abe37cfafe9fe22eae38cdfd0c36d7e5c0b47a3e2b406e3e59a781b74f71'),
              ('eb', '8db3749c71de096ef466fa1763801478bb004898ca5ca895ec41f9a45cf61dc8'),
              ('fj', 'f6915d6f93be658d55e0a5673fc6b302e84a6cdbdb9ef3b02735c5327e10009a')]
    for tag, expected in stages:
        script = R/f'tools/audit/record_roster49_progress_{tag}.py'
        text = b.decode('cp1252').replace('\r\n', '\n') + literal_append(script)
        b = text.replace('\n', '\r\n').encode('cp1252')
        history.append(dict(append_script=str(script.relative_to(R)), bytes=len(b), sha256=sha(b), expected=expected))
        print('APPEND', tag, len(b), sha(b), sha(b)==expected)
        assert sha(b) == expected
    target = V/'root49-QA-recovery-fr-exact-fj.md'
    assert not target.exists() or target.read_bytes() == b
    target.write_bytes(b)
    (V/'root49-QA-recovery-fr-replay.json').write_text(json.dumps(history, indent=2)+'\n', encoding='utf-8')
    print('EXACT_RECOVERED_BACKUP', str(target), sha(b))

if __name__ == '__main__':
    main()
