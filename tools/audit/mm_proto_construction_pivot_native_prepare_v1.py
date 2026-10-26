"""Bind one unchanged-observer MegaEasy450 pivot pilot to actual current3b."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D / 'mm-proto-construction-pivot-candidate-v9'
BASE = D / 'root-presentation450-3b112-v1'
EXPECTED = '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
SOURCE = 'fb2f1aca3a9c60446a2fdbd6df772eb8da6b3ed737c578fe274dc49fcb0a628e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--packet', type=Path, required=True)
    a = ap.parse_args()
    ready = a.packet / 'readiness.json'
    assert not (a.packet / 'launch.json').exists() and not (a.packet / 'base-readiness.json').exists()
    q = json.loads(ready.read_text())
    assert q['passed'] and not q['native_run'] and q['ROM_sha256'] == EXPECTED
    source = B / 'ready-v1/readiness.json'
    assert sha(source) == SOURCE
    s = json.loads(source.read_text())
    assert s['passed'] and s['source_only'] and s['candidate_ROM_sha256'] == EXPECTED
    deps = {Path(p): h for p, h in q['bindings'].items()}
    deps.update({Path(p): h for p, h in json.loads((source.parent / 'bindings.json').read_text()).items()})
    for p, h in deps.items():
        assert sha(p) == h, p
    baseline = json.loads((BASE / 'native-receipt.json').read_text())
    assert baseline['passed'] and baseline['ROM_sha256'] == s['parent_ROM_sha256']
    assert baseline['result']['completed_DMAs'] == 402
    cfg, old = [json.loads((p / 'config.json').read_text()) for p in [a.packet, BASE]]
    for key in ['limit', 'hooks', 'ram', 'smc']:
        assert cfg[key] == old[key], key
    assert cfg['limit'] == 450 and cfg['hooks']['DmaComplete']['pc'] == 0xe008
    assert (a.packet / 'prefix.csv').read_bytes() == (BASE / 'prefix.csv').read_bytes()
    assert q['environment'] == json.loads((BASE / 'readiness.json').read_text())['environment']
    plan = '''ONE unlaunched natural MegaEasy450 opening, exact0a7dd candidate.
The actual current3b ROOT450,402DMAs/275wholePPU/72safeenables, is the matched
reference. Same450poll-index controller prefix, unchanged qualified observer,
actualE008/full256physicalDMA source/destination/strictdisable-render/deadline,
NMIAXY-SP/5SMC/CHR/IRQ31 checks, isolated runtime/settings and8-sprite limit.
No source/actor/resource/menu/audio/RNG outcome injection or new observer code.
275wholePPU frames176..450 plus raw timing, input and every DMA are retained.

After one explicit ROOT grant and one attempt, preserve everyFALSE/no retry.
Compare true cumulative DMA epochs at matched450cutoffs and net402reference;
changed physical OAM/pixels are intentional and must not be asserted byteexact.
Review paired complete images, including admitted early-game body/shot/world
tradeoffs. This unchanged module does not log per-live-slot identities/ages,
full CHR/palette per frame or construction phase, so do not invent that data or
claim all-publication/per-live-shot fairness. Any sprite budget derivation
must use actual16-high CTRL where present, not obsolete8-high assumptions.

Source controls retain every sprite part/order modulo the image delta, all
physics/resource/source-engine states and caller ABI. Conservative contiguity
fallback means alternate draw phases need not produce alternate priorities.
Changing shot counts need not place body0. Owned Main+22..174 andcommonMoveAll
+16cycles are risks; no NMI work/newRAM or timing acceptance exists yet. Vine
and lifts are source-qualified partial producers but are not in this450level
opening. No Proto/charged/fullroute/otherlevels/allroster native coverage.
'''
    (a.packet / 'PLAN.txt').write_text(plan)
    shutil.copyfile(ready, a.packet / 'base-readiness.json')
    extra = {Path(__file__), source, source.parent / 'catalog.json', source.parent / 'bindings.json',
             R / 'tools/audit/presentation_timing_launch_v1.py',
             R / 'tools/audit/mm_proto_basic_remainder_native_review_v1.py',
             R / 'tools/audit/mm_proto_priority450_review_v1.py'}
    extra |= {BASE / name for name in ['readiness.json', 'native-receipt.json', 'config.json', 'prefix.csv',
               'result.json', 'launch.json', 'timing.jsonl', 'direct-index.csv', 'direct.argb']}
    extra |= {p for p in a.packet.iterdir() if p.is_file() and p.name != 'readiness.json'}
    deps.update({p: sha(p) for p in extra})
    final = q | dict(native_grant=False, maximum_launches=1, maximum_workers=1,
        source_readiness_sha256=SOURCE, source_readiness=str(source),
        actual_current3b_reference=True, reference_DMAs=402, exact_module_input_hooks_and_guards=True,
        physical_OAM_pixel_equality_not_expected=True, no_new_observer_code=True, limits=plan,
        bindings={str(p.resolve()): h for p, h in sorted(deps.items())})
    put(ready, final)
    proof = dict(passed=True, prepared_only=True, native_run=False, native_grant=False,
        ROM_sha256=EXPECTED, readiness_sha256=sha(ready), source_readiness_sha256=SOURCE,
        bindings=len(deps), maximum_launches=1, maximum_workers=1,
        command=q['command'], launcher=str(R / 'tools/audit/presentation_timing_launch_v1.py'),
        launcher_sha256=sha(R / 'tools/audit/presentation_timing_launch_v1.py'), tool_sha256=sha(__file__))
    put(a.packet / 'preparation.json', proof)
    put(a.packet / 'catalog.json', {p.name: dict(bytes=p.stat().st_size, sha256=sha(p))
                                  for p in sorted(a.packet.iterdir()) if p.is_file()})
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
