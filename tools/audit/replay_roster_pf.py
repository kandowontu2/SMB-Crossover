"""Sequential independent direct replays of retained clean discoveries.

This wrapper leaves the pinned capture and strict reviewers unchanged. A raw
review rejection remains recorded even if a separate read-only native observer
subsequently proves the exact temporary projectile origin responsible for it.
"""
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
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--discoveries', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    source = json.loads(a.discoveries.read_text())
    digest = sha(a.rom)
    assert source['ROM_sha256'] == digest and source['phase'] == 'discover'
    cases = [q for q in source['runs'] if q['passed']]
    assert cases and len({(q['identity'], q['mode']) for q in cases}) == len(cases)
    drivers = {
        'capture': ROOT / 'tools/audit/capture_direct_replay_ot.py',
        'review': ROOT / 'tools/audit/review_direct_route_pa.py',
        'guard': ROOT / 'tools/audit/reproduce_sophia_lock_og.py',
    }
    assert sha(drivers['capture']) == '6d4729e57233d235d2beae53d9d492428831337a86cc9294fda6c2b0be607534'
    report = dict(passed=False, complete=False, goal_complete=False,
                  ROM_sha256=digest, discovery_index_sha256=sha(a.discoveries),
                  driver_hashes={k: sha(v) for k, v in drivers.items()},
                  wrapper_sha256=sha(Path(__file__)), native_workers=1,
                  selected_cases=len(cases), runs=[],
                  scope='Independent exact same-hash input/trace replays with every actual PPU frame retained losslessly. Strict original motion/CHR/split bounds remain unchanged; separately observed native temporary origins only. Sampled overviews are not exhaustive human visual review or every-item/source-fidelity completion.')

    def save():
        (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')

    def call(label, command):
        with (out / (label + '.log')).open('w') as log:
            return subprocess.run([sys.executable, *map(str, command)], cwd=ROOT,
                                  stdout=log, stderr=subprocess.STDOUT).returncode

    save()
    for case in cases:
        name, mode = case['identity'], case['mode']
        key = name + '-' + mode
        route = Path(case['folder'])
        assert sha(route / 'manifest.json') == case['manifest_sha256']
        capture, review, guard = [out / (prefix + key) for prefix in ('direct-', 'review-', 'guard-')]
        entry = dict(identity=name, mode=mode, passed=False, discovery=str(route),
                     discovery_manifest_sha256=sha(route / 'manifest.json'),
                     capture=str(capture), review=str(review))
        report['runs'].append(entry)
        entry['capture_exit'] = call('capture-' + key, [drivers['capture'], '--rom', a.rom,
                                     '--route', route, '--output', capture])
        if entry['capture_exit'] == 0:
            args = [drivers['review'], '--rom', a.rom, '--capture', capture,
                    '--discovery', route, '--output', review]
            entry['raw_review_exit'] = call('review-' + key, args)
            if entry['raw_review_exit'] == 0:
                entry['passed'] = True
            else:
                entry['guard_exit'] = call('guard-' + key, [drivers['guard'], '--rom', a.rom,
                    '--route', route, '--output', guard, '--expect', 'repaired', '--until-clear', '--movement'])
                if entry['guard_exit'] == 0:
                    guarded_review = out / ('guarded-review-' + key)
                    entry['guarded_review_exit'] = call('guarded-review-' + key,
                        args[:-1] + [guarded_review, '--guard', guard])
                    entry['passed'] = entry['guarded_review_exit'] == 0
                    entry['guarded_review'] = str(guarded_review)
        if entry['passed']:
            proof_path = Path(entry.get('guarded_review', str(review))) / 'proof.json'
            proof = json.loads(proof_path.read_text())
            assert proof['passed'] and proof['ROM_sha256'] == digest
            entry['strict_proof_sha256'] = sha(proof_path)
        save()
        print(json.dumps(dict(completed=len(report['runs']), total=len(cases), **entry)), flush=True)
    report['complete'] = True
    report['passed'] = all(q['passed'] for q in report['runs'])
    save()
    (out / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
