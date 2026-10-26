"""Freeze the finite source-qualified foreground pivot, without native launch."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import shutil
import sys
import mm_proto_construction_pivot_cpu_v5 as cpu

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'root-current-roster-composition-v1'
B = D / 'mm-proto-construction-pivot-candidate-v9'
EXPECTED = '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, v):
    p.write_text(json.dumps(v, indent=2) + '\n')


def imports(paths):
    found = set()
    while paths:
        p = paths.pop().resolve()
        if p in found:
            continue
        found.add(p)
        if p.suffix != '.py':
            continue
        for node in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))):
            names = ([q.name for q in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for name in names:
                for directory in [p.parent, R / 'tools/audit', R / 'tools']:
                    local = directory / (name.replace('.', '/') + '.py')
                    if local.is_file():
                        paths.append(local)
                        break
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(B / 'candidate.nes') == EXPECTED
    refs = ['cpu-v5', 'callers-v5', 'mixed-v1', 'build-controls-v1']
    proofs = {}
    deps = {Path(sys.executable), P / 'source-manifest.json', B / 'source-manifest.json',
            B / 'source.patch', B / 'proof.json', B / 'build.json'}
    for directory in [P, B]:
        manifest = json.loads((directory / 'source-manifest.json').read_text())
        for rel, h in manifest.items():
            p = directory / 'source' / rel
            assert sha(p) == h
            deps.add(p)
        deps |= {directory / ('candidate' + ext) for ext in ['.nes', '.dbg', '.lbl', '.map']}
    for name in refs:
        p = B / name / 'proof.json'
        proof = json.loads(p.read_text())
        assert proof['passed'] and proof['candidate_ROM_sha256'] == EXPECTED
        proofs[name] = dict(path=str(p), sha256=sha(p))
        shutil.copyfile(p, a.output / (name + '-proof.json'))
        deps |= {p} | {q for q in p.parent.iterdir() if q.suffix == '.json'}
    old, new = [cpu.fixture.scoped_load(q / 'candidate.nes') for q in [P, B]]
    foreign = []
    for char in [0, 2, 3, 18]:
        for groups in [1, 2]:
            foreign.append(cpu.partial(old, new, dict(entry='DrawAllMetasprites', char=char,
                variant=0, types=[1] * 4, priorp=0, first=0, shuffle=0, flags=0x61), groups))
    assert all(q['cycle_delta'] < 0 for q in foreign)
    put(a.output / 'foreign-Vine-cases.json', foreign)
    reads = []
    for p in (P / 'source/src').rglob('*'):
        if p.suffix not in ['.s', '.inc']:
            continue
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines):
            if re.match(r'\s*(lda|ldx|ldy)\s+GuestOamRotationActive\s*(?:;.*)?$', line):
                following = next(s.strip() for s in lines[i + 1:] if s.strip() and not s.strip().startswith(';'))
                assert following.startswith('beq '), (p, i, following)
                reads.append(dict(file=p.relative_to(P / 'source').as_posix(), line=i + 1,
                                  read=line.strip(), following=following, source_sha256=sha(p)))
    assert len(reads) == 21
    assert 'USE_SMB2J_FEATURES=0' in (B / 'source/build_options.ini').read_text()
    assert 'MOUSE_DISPLAY_CURSOR=0' in (B / 'source/build_options.ini').read_text()
    before, after = [(q / 'candidate.nes').read_bytes() for q in [P, B]]
    assert before[16 + 128 * 8192:] == after[16 + 128 * 8192:]
    assert all(before[16 + bank * 8192:16 + (bank + 1) * 8192] ==
               after[16 + bank * 8192:16 + (bank + 1) * 8192]
               for bank in range(128) if bank not in [0, 4, 26, 66])
    put(a.output / 'owner-readers.json', dict(passed=True, reads=reads, no_new_RAM=True,
        lifecycle='Existing owner0/1 remains boolean to every old reader. Owned image delta is4-aligned in bits2..7. Full Draw begins at1; phase/active/contiguity failures retain1. MoveAll clears only delta while retaining old boolean, +16foregroundcycles. Menu/character init writes0; reset RAM init clears it. No-draw Main retains the mapping; translated Vine/lift writers restore logical cursor and actual source ABI. No NMI work/state added.',
        partial_bound='Native reservation40 + at most five24B lifts + two24B Vine groups =208 logical end. Mapped reservation<=88 admits all168B through last physical byte255. Every Main reobtains reservation40; partial offsets do not accumulate across no-draw Main turns.',
        direct_writer_audit='Native Vine and small-lift writers translated. ENABLE_CROSSOVER removes direct brick chunks/firebar OAM; these emit through DrawAll cached/metasprite paths. Hammers/large platforms/powerups/blocks/coins/enemy/flagpole write actor records. SimulateWind is disabled by USE_SMB2J_FEATURES0. Reset/cold/menu use MoveAll or their existing owner0 initialization. Fast Goomba/water and flash/flip emit within complete DrawAll; foreign-specific kernels see old0/1. MMC3 page sanitation is compiled out; ordinary builds exact. This is source ownership/finite producer evidence, not universal static call reachability.',
        NMI_PRG125_127_all_other_banks_and_CHR_exact=True))
    owned = [R / 'tools/audit' / name for name in [
        'mm_proto_construction_pivot_candidate_v9.py', 'mm_proto_construction_pivot_cpu_v5.py',
        'mm_proto_construction_pivot_callers_v5.py', 'mm_proto_construction_pivot_mixed_v1.py',
        'mm_proto_construction_pivot_build_controls_v1.py', Path(__file__).name]]
    deps |= imports(owned[:])
    report = R / 'docs/qa/mm-proto-construction-pivot-2026-10-26.txt'
    assert report.is_file()
    deps.add(report)
    negatives = [D / f'mm-proto-construction-pivot-candidate-v{v}/failure.json' for v in [1, 2, 3, 4, 5, 7]]
    negatives += [D / 'mm-proto-construction-pivot-candidate-v3/cpu-v2/failure.json',
                  D / 'mm-proto-construction-pivot-candidate-v6/cpu-v3/failure.json',
                  B / 'callers-v1/failure.json', B / 'callers-v2/failure.json']
    present = [p for p in negatives if p.is_file()]
    put(a.output / 'retained-negatives.json', {str(p): sha(p) for p in present})
    deps |= set(present)
    deps |= {q for q in a.output.iterdir() if q.is_file()}
    put(a.output / 'bindings.json', {str(p.resolve()): sha(p) for p in sorted(deps)})
    proof = dict(passed=True, source_only=True, native_run=False, native_grant=False,
        parent_ROM_sha256=sha(P / 'candidate.nes'), candidate_ROM_sha256=EXPECTED,
        changed_source=json.loads((B / 'proof.json').read_text())['changed_source'],
        changed_ROM_bytes=1336, changed_banks=[0, 4, 26, 66], proofs=proofs,
        foreign_Vine_cases=len(foreign), foreign_Vine_cycles=[-38, -76], existing_boolean_readers=21,
        owned_draw_cycles=[22, 174], foreign_draw_cycles=[-23, 0], owned_Vine_cycles_per_group=36,
        direct_lift_cycles={'foreign': -156, 'translated': -87}, MoveAll_foreground_cycles=16,
        NMI_added_cycles=0, new_RAM_bytes=0, canonical_and_both_ordinary_exact=True,
        source_manifest_sha256=sha(B / 'source-manifest.json'), patch_sha256=sha(B / 'source.patch'),
        bindings_sha256=sha(a.output / 'bindings.json'), bindings=len(deps),
        limits='No native draw/cadence/pixel/publication qualification. Alternating constructions and contiguity fallback cannot guarantee displayed alternation. Stable shot count can put body first; changing shot counts may not. Shots/world retain original relative order but may lose hardware selection on body-priority constructions. +22..174owned Main and+16common MoveAll are real costs; source-only pass is not performance/adoption. B/U model bits and dead top stack are explicitly excluded only where the true IRQ/physical-flags oracle requires; no native DMA mask exists.',
        tool_sha256=sha(__file__))
    put(a.output / 'readiness.json', proof)
    put(a.output / 'catalog.json', {p.name: dict(bytes=p.stat().st_size, sha256=sha(p))
                                  for p in sorted(a.output.iterdir()) if p.is_file()})
    print(json.dumps(dict(passed=True, readiness_sha256=sha(a.output / 'readiness.json'),
                          bindings=len(deps), output=str(a.output)), indent=2))


if __name__ == '__main__':
    main()
