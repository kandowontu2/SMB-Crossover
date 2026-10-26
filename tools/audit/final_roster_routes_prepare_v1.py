"""Prepare existing qualified controllers for a fresh roster run; never launch.

Historical clears qualify controller selection, not a different ROM. The actual
new run and independent replay are still required for every selected identity.
"""
from pathlib import Path
import argparse, hashlib, json, re, sys

from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OLD = D / 'current3cee-eight-routes-v1'
LUIGI = D / 'luigi-profile641-corridor-route-ready-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def put(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--cases', nargs='+', help='Optional subset: identity:easy|hard')
    a = p.parse_args()
    rom, out = a.rom.resolve(), a.output.resolve()
    assert sha(rom) == a.expected_sha256
    assert not out.exists() and not out.is_relative_to(ROOT)
    source_proofs = [ROOT / 'docs/qa/checkpoints/2026-10-26' / name / 'proof.json'
                     for name in ['current3cee-eight-routes-v1', 'current3cee-remaining27-v1']]
    qualified = []
    dependencies = {Path(__file__), *source_proofs, OLD / 'coordinator.py',
                    OLD / 'runner.py', OLD / 'capture.py'}
    for f in source_proofs:
        q = read(f)
        assert q['passed']
        qualified.extend(q['profiles'])
    # Chip/Dale were the earlier two-route anchor, separate from eight+27.
    anchor = ROOT / 'docs/qa/checkpoints/2026-10-26/current37-1-1-v1/proof.json'
    combined = read(anchor)
    assert combined['ordinary_selected_route_clear_and_replay_complete']
    dependencies.add(anchor)
    for r in combined['rows']:
        if r['identity'] not in ['chip', 'dale']:
            continue
        direct = Path(r['proof_path']).parent
        assert direct.name.endswith('-direct')
        qualified.append(dict(case=r['identity'] + '-' + r['mode'],
                              discovery=str(direct.with_name(direct.name[:-7])),
                              direct=str(direct), direct_proof_sha256=r['proof_sha256']))
    assert len(qualified) == len({r['case'] for r in qualified}) == 37
    luigi = read(LUIGI / 'native-proof.json')
    assert luigi['passed'] and len(luigi['results']) == 2
    assert all(r['passed'] and r['evidence']['result']['cleared']
               and r['evidence']['result']['deaths'] == 0 for r in luigi['results'])
    dependencies.add(LUIGI / 'native-proof.json')
    out.mkdir(parents=True)
    preview = out / 'expected-policies'
    preview.mkdir()
    b = scoped_load(rom)
    catalog, mapping = [], []
    for q in qualified:
        name, mode = q['case'].rsplit('-', 1)
        assert mode in ['easy', 'hard']
        folder = Path(q['discovery'])
        record = folder / 'manifest.json'
        direct = Path(q['direct']) / 'proof.json'
        assert sha(direct) == q['direct_proof_sha256'] and read(direct)['passed']
        if name == 'luigi':
            folder = LUIGI / 'discovery'
            record = folder / 'native-receipt.json'
        else:
            result = read(record)['result']
            assert result['cleared'] and result['deaths'] == 0
        source = folder / 'policy.lua'
        body = source.read_text(encoding='utf-8')
        assert body.startswith('dofile('), source
        body = body.split('\n', 1)[1]
        assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', body)
        changes = []
        def bind(m):
            n, old = m[1], int(m[2])
            if n not in b['syms']:
                return m[0]
            value = address(b, n)
            changes.append(dict(symbol=n, old=old, actual=value))
            return 'L.' + n + '=' + str(value)
        rebound = re.sub(r'^L\.(\w+)=(\d+)\s*$', bind, body, flags=re.M)
        f = preview / (q['case'] + '-policy.lua')
        f.write_text('dofile(' + lua((out / 'native/native-guard.lua').as_posix()) + ')\n'
                     + rebound, encoding='utf-8')
        catalog.append(dict(identity=name, mode=mode, discovery=str(record)))
        mapping.append(dict(case=name + ':' + mode, source_policy=str(source),
                            source_sha256=sha(source), source_record=str(record),
                            source_record_sha256=sha(record), preview=str(f),
                            preview_sha256=sha(f), RAM_rebinding=changes,
                            retained_corrected_policy=name in ['bill', 'simon', 'luigi', 'zelda2']))
        dependencies.update([source, record, direct, f])
    cases = [q['case'] for q in mapping]
    selected = a.cases or cases
    assert len(selected) == len(set(selected)) and all(q in cases for q in selected)
    put(out / 'selected-aggregate.json', dict(runs=catalog, historical_controllers_only=True))
    text = (OLD / 'coordinator.py').read_text(encoding='utf-8')
    text, count = re.subn(r'^    aggregate_path = Path\([^\n]+\)$',
                         lambda _: '    aggregate_path = Path(' + repr(str(out / 'selected-aggregate.json')) + ')',
                         text, flags=re.M)
    assert count == 1
    old = "        if name == 'zelda2':\n            body = stair_controller(body)\n"
    assert text.count(old) == 1
    text = text.replace(old, '        # Catalogue already contains the qualified Zelda II stair wrapper.\n')
    compile(text, 'coordinator.py', 'exec')
    (out / 'coordinator.py').write_text(text, encoding='utf-8')
    put(out / 'policy-map.json', mapping)
    sys.path.insert(0, str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    runtime = LuaRuntime()
    for f in sorted(preview.glob('*.lua')):
        runtime.compile(f.read_text(encoding='utf-8'))
    dependencies.add(Path(sys.modules[LuaRuntime.__module__].__file__))
    delta = int(b['syms']['GameLoop']['size'], 0) - 1
    assert b['raw'][location(b, 'GameLoop') + delta] == 0x60
    command = [sys.executable, '-B', str(out / 'coordinator.py'), '--rom', str(rom),
               '--archive', str(D), '--output', str(out / 'native'), '--cases', *selected,
               '--replay', '--frames', '18000']
    for suffix in ['.nes', '.dbg', '.lbl', '.map']:
        dependencies.add(rom.with_suffix(suffix))
    dependencies.update(f for f in out.iterdir() if f.is_file())
    put(out / 'readiness.json', dict(prepared=True, native_run=False, ROM_sha256=sha(rom),
        all_identity_controller_count=37, cases=selected, command=command, maximum_workers=1,
        Lua54_controller_syntax_checks=37, qualified_stair_wrapper_added_again=False,
        maximum_native_launches=2 * len(selected), automatic_retries=0,
        bindings={str(f.resolve()):sha(f) for f in sorted(dependencies)},
        limits='Preparation only. Existing native/replay harnesses, qualified corrected controllers '
               'and dynamic RAM bindings are reused; no old clear is credited to the new ROM. '
               'Actual difficulty readback, completed-loop motion and body CHR checks remain. '
               'All current physical items, graphics, sound and performance require their own evidence. '
               'Before execution, bind the final repaired source/environment and inspect the selected '
               'plan; respect the project-wide two-worker cap. Failures are retained, never auto-retried.'))
    print(json.dumps(dict(prepared=True, native_run=False, identities=37,
                         selected=len(selected), readiness_sha256=sha(out / 'readiness.json'))))


if __name__ == '__main__':
    main()
