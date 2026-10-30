"""Finish the genuine v2 link receipt after correcting only its dependency parser."""
from pathlib import Path
import json
import re
import prepare_ff_current_component_v1 as C
from prepare_ff_current_component_v2 import qualified

O = C.R/'build/final-fantasy-current-component-v2'


def dependencies(path):
    raw = path.read_text().replace('\\\n', ' ').replace('\\ ', '\0').splitlines()[0]
    parts = re.split(r':\s+', raw, maxsplit=1)
    assert len(parts) == 2, path
    result = [Path(value.replace('\0', ' ')).resolve() for value in parts[1].split()]
    assert result and all(p.is_file() for p in result), path
    return result


if __name__ == '__main__':
    proof_path = O/'build-proof.json'
    assert not proof_path.exists()
    original = (C.P/'candidate.nes').read_bytes()
    assert C.sha(C.P/'candidate.nes') == '753b6bd1e51bb6c427206f841e63790bfd79fe2a3cca964e04254408f87ead53'
    assert (O/'reproduce/candidate.nes').read_bytes() == original
    raw = (O/'linked/candidate.nes').read_bytes()
    assert len(raw) == len(original) == 2097168
    assert raw == (C.R/'build/final-fantasy-current-component-v1/linked/candidate.nes').read_bytes()
    old = qualified(C.P/'candidate.nes')
    new = qualified(O/'linked/candidate.nes')
    assert all(new['syms'].get(name, {}).get('val') == sym['val'] for name, sym in old['syms'].items())
    changes = [i for i, (a, b) in enumerate(zip(original, raw)) if a != b]
    leases = [dict(name='FINAL_FANTASY_CORE', start=16+62*8192+0xa00, size=0xc90, fill=255, reference='component.bin'),
              dict(name='FINAL_FANTASY_ART', start=16+93*8192+0x1000, size=4096, fill=255, reference='art.bin'),
              dict(name='FINAL_FANTASY_CHR', start=1048592+756*1024, size=32768, fill=0, reference='chr.bin')]
    for lease in leases:
        lo, hi = lease['start'], lease['start']+lease['size']
        assert original[lo:hi] == bytes([lease['fill']])*lease['size'], lease
        lease['changed_bytes'] = sum(lo <= i < hi for i in changes)
        reference = C.OLD/lease['reference']
        payload = reference.read_bytes()
        assert raw[lo:lo+len(payload)] == payload
        lease['actual_payload_bytes'] = len(payload)
        lease['payload_sha256'] = C.sha(reference)
    assert sum(x['changed_bytes'] for x in leases) == len(changes)
    old_component = (C.OLD/'component.s').read_text()
    names = re.findall(r'^(\w+)=', old_component.split('.macpack')[0], re.M)
    source = (O/'linked/ff-component.s').read_text()
    imports = {}
    for name in names:
        symbol = old['syms'][name]
        directive = '.importzp' if symbol['addrsize'] == 'zeropage' else '.import'
        assert directive+' '+name+'\n' in source
        assert not re.search(r'^'+name+r'\s*=', source, re.M)
        assert new['syms'][name]['val'] == symbol['val']
        imports[name] = dict(value=symbol['val'], address_size=symbol['addrsize'])
    deps = set()
    commands = []
    files = []
    for stage in ['reproduce', 'linked']:
        directory = O/stage
        log = json.loads((directory/'compile-log.json').read_text())
        assert log and all(row['returncode'] == 0 for row in log)
        commands += log
        deps.update(dependencies(directory/'main.d'))
        if stage == 'linked':
            deps.update(dependencies(directory/'ff.d'))
        files += [p for p in directory.iterdir() if p.is_file()]
    recipes = json.loads((C.P/'compile-log.json').read_text())
    deps.update(Path(v) for row in recipes for v in row['command'] if v.endswith('.o') and Path(v).is_file())
    negative = O/'dependency-parser-negative.json'
    C.write(negative, json.dumps(dict(
        status='RETAINED_METADATA_PARSER_NEGATIVE_NO_PRODUCT_CHANGE',
        cause='ca65 uses colon plus TAB and a second phony-target rule. The original parser required a space; the first correction also parsed phony targets as dependencies. Read only the logical first rule.',
        corrected_pattern=r':\s+', actual_dependency_files=len(deps),
        link_succeeded_before_parser_failure=True,
        no_rebuild_or_binary_change_for_parser_fix=True), indent=2)+'\n')
    files += [Path(__file__).resolve(), Path(C.__file__).resolve(),
              C.R/'tools/audit/prepare_ff_current_component_v2.py',
              C.R/'build/final-fantasy-current-component-v1/symbol-alias-negative.json',
              negative, O/'finalizer-parser-negative-v3.py', C.P/'compile-log.json', C.P/'candidate.nes', C.P/'candidate.dbg',
              C.OLD/'component.s', C.OLD/'handoff.json', C.OLD/'controls.json', C.OLD/'assets.json',
              *[C.OLD/x['reference'] for x in leases]]
    bindings = {str(p.resolve()): C.sha(p) for p in set(files) | deps}
    proof = dict(passed=True, native=False, source_only=True, shared_installation=False,
                 status='CURRENT_HOST_GENUINE_FF_COMPONENT_LINK_NO_ADMISSION',
                 parent_ROM_sha256=C.sha(C.P/'candidate.nes'), ROM_sha256=C.sha(O/'linked/candidate.nes'),
                 exact_parent_source_reproduction=True, qualified_old_symbol_pairs=len(old['syms']),
                 old_symbol_moves=0, unchanged_all_other_PRG_header_CHR=True,
                 changed_bytes=len(changes), leases=leases,
                 genuine_host_imports=imports, actual_dependencies=len(deps),
                 original_component_CORE_ART_CHR_byte_exact=True,
                 limits=['FF remains pending; host terrain/combat/full rendering/palette/music adapters are absent.',
                         'No native run, new Main/ISR qualification, full-powerup route or FPS claim.',
                         'Existing FF leases only; no WRAM or header change.'], bindings=bindings)
    C.write(proof_path, json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(passed=True, ROM_sha256=proof['ROM_sha256'],
                         genuine_imports=len(imports), old_symbols=len(old['syms']),
                         changed_bytes=len(changes), dependencies=len(deps))))
