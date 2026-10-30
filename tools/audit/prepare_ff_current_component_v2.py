"""Use real qualified symbols rather than debugger convenience aliases in v1."""
import json
from pathlib import Path
import prepare_ff_current_component_v1 as C

original_load = C.scoped_load


def qualified(path):
    bundle = original_load(path)
    scopes = {}
    symbols = []
    for line in Path(path).with_suffix('.dbg').read_text().splitlines():
        if not line.startswith(('scope\t', 'sym\t')):
            continue
        fields = dict(part.split('=', 1) for part in line.split('\t', 1)[1].split(',') if '=' in part)
        if line.startswith('scope\t'):
            scopes[fields['id']] = fields
        elif 'val' in fields:
            symbols.append(fields)

    def prefix(key):
        scope = scopes.get(key, {})
        names = ([prefix(scope['parent'])] if 'parent' in scope else []) + [scope.get('name', '').strip('"')]
        return '::'.join(name for name in names if name)

    bundle['syms'] = {}
    for symbol in symbols:
        name = symbol['name'].strip('"')
        parent = prefix(symbol.get('scope'))
        bundle['syms'][parent+'::'+name if parent else name] = symbol
    return bundle


if __name__ == '__main__':
    failed = C.O
    assert (failed/'linked/candidate.nes').is_file()
    old, new = qualified(C.P/'candidate.nes'), qualified(failed/'linked/candidate.nes')
    assert all(new['syms'].get(name, {}).get('val') == value['val'] for name, value in old['syms'].items())
    convenience_old, convenience_new = original_load(C.P/'candidate.nes'), original_load(failed/'linked/candidate.nes')
    false_moves = {name: [value['val'], convenience_new['syms'].get(name, {}).get('val')]
                   for name, value in convenience_old['syms'].items()
                   if convenience_new['syms'].get(name, {}).get('val') != value['val']}
    assert false_moves and all(name not in old['syms'] for name in false_moves)
    negative = dict(status='RETAINED_V1_ASSERTION_NEGATIVE_NOT_A_PRODUCT_RELOCATION',
                    cause='Convenience loader aliases unqualified procedure-local names such as Loop and Yes; adding a module changes which alias wins.',
                    actual_qualified_symbol_pairs=len(old['syms']), actual_symbol_moves=0,
                    rejected_convenience_alias_moves=false_moves,
                    inputs={str(p): C.sha(p) for p in [Path(C.__file__).resolve(), C.P/'candidate.nes', C.P/'candidate.dbg',
                                                        failed/'linked/candidate.nes', failed/'linked/candidate.dbg', failed/'linked/compile-log.json']})
    C.write(failed/'symbol-alias-negative.json', json.dumps(negative, indent=2)+'\n')
    C.O = C.R/'build/final-fantasy-current-component-v2'
    C.scoped_load = qualified
    C.main()
    proof_path = C.O/'build-proof.json'
    proof = json.loads(proof_path.read_text())
    assert C.sha(C.O/'linked/candidate.nes') == C.sha(failed/'linked/candidate.nes')
    proof['qualified_old_symbol_pairs'] = len(old['syms'])
    proof['retained_negative'] = str(failed/'symbol-alias-negative.json')
    for path in [Path(__file__).resolve(), failed/'symbol-alias-negative.json']:
        proof['bindings'][str(path)] = C.sha(path)
    C.write(proof_path, json.dumps(proof, indent=2)+'\n')
