"""Compact source/native review checkpoint; no ROM/audio/raw/settings copies."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D / 'mm-proto-construction-pivot-candidate-v9'
N = D / 'mm-proto-construction-pivot-native-ready-v1'
V = D / 'mm-proto-construction-pivot-native-review-v1'
PIX = D / 'mm-proto-construction-pivot-pixels-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, v):
    p.write_text(json.dumps(v, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    source_ready = B / 'ready-v1/readiness.json'
    assert sha(source_ready) == 'fb2f1aca3a9c60446a2fdbd6df772eb8da6b3ed737c578fe274dc49fcb0a628e'
    assert sha(N / 'readiness.json') == 'd972b8aff1e6f636a5e0604e8ff766f1a43299caf728d4b07e58662908ce5505'
    bindings = json.loads((B / 'ready-v1/bindings.json').read_text())
    bindings.update(json.loads((N / 'readiness.json').read_text())['bindings'])
    bindings.update(json.loads((V / 'bindings.json').read_text()))
    bindings.update(json.loads((PIX / 'bindings.json').read_text()))
    for p, h in bindings.items():
        assert sha(p) == h, p
    result = json.loads((V / 'proof.json').read_text())
    assert result['native_no_harm_cadence_pass'] and result['active_OAM_multiset_equal_pairs'] == 275
    assert result['different_RGB_pairs'] == 28
    copies = [(B / 'source.patch', 'source.patch'), (B / 'proof.json', 'source-layout-proof.json'),
              (source_ready, 'source-aggregate-proof.json'), (N / 'native-receipt.json', 'native-receipt.json'),
              (N / 'result.json', 'native-result.json'), (V / 'proof.json', 'native-comparison.json'),
              (V / 'all275-paired-observations.json', 'all275-observations.json'),
              (PIX / 'proof.json', 'color-metric-proof.json'), (PIX / 'all79-color-counts.json', 'all79-color-counts.json'),
              (B / 'ready-v1/owner-readers.json', 'source-ownership.json'),
              (B / 'ready-v1/retained-negatives.json', 'retained-negatives.json')]
    for name in ['cpu-v5', 'callers-v5', 'mixed-v1', 'build-controls-v1']:
        copies.append((B / name / 'proof.json', name + '-proof.json'))
    for number in range(1, 5):
        copies.append((PIX / f'all-changed-wholeframe-pairs-{number}.png', f'actual-paired-changed-{number}.png'))
    copies.append((V / 'paired-ending-wholeframes.png', 'actual-paired-residual-ending.png'))
    reports = [R / 'docs/qa' / name for name in ['mm-proto-construction-pivot-2026-10-26.txt',
                                                'mm-proto-construction-pivot-native-2026-10-26.txt']]
    for p in reports:
        copies.append((p, p.name))
    names = ['mm_proto_construction_pivot_candidate_v9.py', 'mm_proto_construction_pivot_cpu_v5.py',
             'mm_proto_construction_pivot_callers_v4.py', 'mm_proto_construction_pivot_callers_v5.py',
             'mm_proto_construction_pivot_mixed_v1.py', 'mm_proto_construction_pivot_build_controls_v1.py',
             'mm_proto_construction_pivot_freeze_v1.py', 'mm_proto_construction_pivot_native_prepare_v1.py',
             'mm_proto_construction_pivot_native_review_v1.py', 'mm_proto_construction_pivot_pixels_v1.py',
             Path(__file__).name]
    owned = [R / 'tools/audit' / name for name in names]
    for p in owned:
        copies.append((p, 'frozen-tools/' + p.name))
    for original, relative in copies:
        dest = a.output / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, dest)
        bindings[str(original.resolve())] = sha(original)
    raw = [N / name for name in ['timing.jsonl', 'direct.argb', 'direct-index.csv', 'prefix.csv', 'run.lua',
                                  'ROOT-grant.json', 'launch.json', 'native-host.log', 'native-receipt.json',
                                  'readiness.json', 'config.json', 'result.json']]
    put(a.output / 'external-artifacts.json', {str(p.resolve()): dict(bytes=p.stat().st_size, sha256=sha(p))
                                            for p in raw + [B / 'candidate.nes', B / 'source-manifest.json']})
    put(a.output / 'changed-source-hashes.json', {rel: dict(parent=sha(D / 'root-current-roster-composition-v1/source' / rel),
                                                           candidate=sha(B / 'source' / rel))
                                               for rel in json.loads((B / 'proof.json').read_text())['changed_source']})
    candidates = [Path(p) for p in bindings if '/tools/audit/' in p.replace('\\', '/') and p.endswith('.py')]
    tracked = set(subprocess.check_output(['git', 'ls-files', '--', *[p.relative_to(R).as_posix() for p in candidates]], cwd=R, text=True).splitlines())
    put(a.output / 'prerequisites.json', {str(p): dict(sha256=sha(p), tracked_now=p.relative_to(R).as_posix() in tracked)
                                        for p in sorted(candidates) if p not in owned})
    put(a.output / 'review-files.json', dict(owned_tools=[p.relative_to(R).as_posix() for p in owned],
        owned_reports=[p.relative_to(R).as_posix() for p in reports], checkpoint=a.output.relative_to(R).as_posix(),
        no_Git_mutation=True, limitations='Explicit staging map only. QA depends on hash-bound local frozen sources, original assets, raw native outputs, compiler/emulator and some working prerequisites. This checkpoint is not turnkey fresh-clone full QA. Exact source patch plus old/new file hashes and frozen builder allow reviewable proposed reconstruction; no production adoption.'))
    (a.output / 'README.txt').write_text('Private Mega/Proto foreground pivot, exact0a7dd on current3b. Not installed.\n'
        'Finite source controls and one450 native timing PASS402vs402, no negative prefixes.\n'
        'Actual visibility is PARTIAL:16frames more blue/cyan,4fewer,59equal;28changed complete pairs viewed.\n'
        'Body improves on some turns while shot selection decreases; residual body loss remains.\n'
        'No per-shot/publication/world fairness, Proto/full-route or adoption claim.\n'
        'All previous source/fixture negatives retained; see two reports and external hashes.\n'
        'No ROM/audio/settings/sourceZIP/raw capture payload copied. No native/Git/source mutation by this builder.\n')
    files = {p.relative_to(a.output).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(a.output.rglob('*')) if p.is_file()}
    assert sum(q['bytes'] for q in files.values()) < 1024 * 1024
    put(a.output / 'catalog.json', files)
    proof = dict(passed=True, checkpoint_only=True, private_not_installed=True, native_launches_by_builder=0,
                 payload_files=len(files), payload_bytes=sum(q['bytes'] for q in files.values()),
                 verified_external_bindings=len(bindings), catalog_sha256=sha(a.output / 'catalog.json'),
                 source_sha256='0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09',
                 finite_native_mechanical_cadence_pass=True, full_visibility_fairness_or_adoption=False,
                 raw_ROM_audio_settings_ZIP_captures_excluded=True, tool_sha256=sha(__file__))
    put(a.output / 'checkpoint-proof.json', proof)
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
