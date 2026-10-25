"""Freeze replay-index snapshots and screen their verified direct PNG sequences."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batches', type=Path, nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    cases, seen, indices = [], set(), []
    for i, source in enumerate(a.batches):
        snapshot = out / ('source-index-' + str(i) + '.json')
        snapshot.write_bytes(source.read_bytes())
        index = json.loads(snapshot.read_text())
        indices.append(dict(source=str(source), frozen=str(snapshot), sha256=sha(snapshot),
                            original_batch_complete=index.get('complete')))
        for case in index['runs']:
            if not case['passed']:
                continue
            key = case['identity'] + '-' + case['mode']
            assert key not in seen
            seen.add(key)
            cases.append(case)
    scanner = ROOT / 'tools/audit/scan_direct_background_ox.py'
    report = dict(scan_complete=False, goal_complete=False, all_graphics_verified=False,
        source_indices=indices, selected_cases=len(cases), scanner_sha256=sha(scanner),
        wrapper_sha256=sha(Path(__file__)), runs=[],
        scope='Snapshot subset of already completed direct independent replay pairs. Every indexed physical-frame PNG is decoded and hashed. Only the existing conservative three-frame transient detector is applied; persistent corruption, sprite/body defects, other graphics, abilities, SFX, source fidelity and exhaustive human review are not certified. Candidate events require investigation.')
    for case in cases:
        key = case['identity'] + '-' + case['mode']
        target = out / key
        with (out / (key + '.log')).open('w') as log:
            code = subprocess.run([sys.executable, str(scanner), '--capture', case['capture'],
                '--output', str(target)], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        result = dict(identity=case['identity'], mode=case['mode'], exit=code, scan_complete=False)
        if code == 0:
            proof = json.loads((target / 'proof.json').read_text())
            assert proof['scan_complete'] and proof['direct_PPU_frames'] and proof['every_PNG_frame_index_hash_exact']
            result.update(scan_complete=True, ROM_sha256=proof['ROM_sha256'],
                retained_frames=proof['retained_PNGs'], triples=proof['admitted_adjacent_triples'],
                candidates=proof['candidate_events'], proof=str(target / 'proof.json'),
                proof_sha256=sha(target / 'proof.json'))
        report['runs'].append(result)
        (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(result), flush=True)
    report['scan_complete'] = all(r['scan_complete'] for r in report['runs'])
    (out / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['scan_complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
