"""Join exact-hash route evidence without erasing unsuccessful attempts."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
OM = ARCHIVE / '2026-10-24-matrix-om'
OJ = ARCHIVE / '2026-10-24-collision-dispatch-oj/probe-v3/routes'
OL = ARCHIVE / '2026-10-24-native-controls-ok/darkwing-recovery-routes-v5'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    digest = sha(a.rom)
    attempts, admitted, references = {}, {}, []
    for directory in (OM / 'matrix-v1', OJ, OL, OM / 'failed-controls-v1'):
        path = directory / 'discover-results.json'
        proof = json.loads(path.read_text())
        assert proof['ROM_sha256'] == digest
        references.append(dict(path=str(path), sha256=sha(path), passed=proof['passed']))
        for case in proof['runs']:
            key = case['identity'] + '-' + case['mode']
            attempts.setdefault(key, []).append(case)
    for path in (OM / 'strict-guarded-v1/proof.json', OM / 'strict-guarded-followup-v1/proof.json'):
        proof = json.loads(path.read_text())
        assert proof['passed'] and proof['ROM_sha256'] == digest
        references.append(dict(path=str(path), sha256=sha(path), passed=True))
        for key, case in proof['admitted'].items():
            assert key not in admitted
            admitted[key] = dict(review=case['review'], review_sha256=case['sha256'], result=case['result'])
    for directory, identity in ((OJ, 'sophia'), (OL, 'darkwing')):
        path = directory / 'route-review.json'
        proof = json.loads(path.read_text())
        assert proof['passed'] and proof['ROM_sha256'] == digest
        references.append(dict(path=str(path), sha256=sha(path), passed=True))
        for key, case in proof['runs'].items():
            if not key.startswith(identity + '-'):
                continue
            assert key not in admitted
            admitted[key] = dict(review=str(path), review_sha256=sha(path), result=case)
    assert len(attempts) == 74 and len(admitted) == 53
    identities = {key.rsplit('-', 1)[0] for key in attempts}
    assert len(identities) == 37
    rows = []
    for identity in sorted(identities):
        for mode in ('easy', 'hard'):
            key = identity + '-' + mode
            assert key in attempts
            row = dict(identity=identity, mode=mode, attempted=True, attempts=attempts[key],
                       strict_independent_replay=key in admitted, every_item_verified=False,
                       exhaustive_human_frame_review=False)
            if key in admitted:
                row['review'] = admitted[key]
            rows.append(row)
    captures = {}
    for key in ('mike-hard', 'bass-easy'):
        path = ARCHIVE / '2026-10-24-direct-capture-ot' / (key + '-v1') / 'proof.json'
        proof = json.loads(path.read_text())
        assert proof['passed'] and proof['ROM_sha256'] == digest
        captures[key] = dict(path=str(path), sha256=sha(path), physical_frames=proof['direct_frames'])
    unresolved = [r['identity'] + '-' + r['mode'] for r in rows if not r['strict_independent_replay']]
    q = dict(ledger_complete=True, all_requested_routes_pass=False, goal_complete=False,
             ROM_sha256=digest, identities=37, attempted_pairs=74, strict_independent_pairs=53,
             pairs_without_clean_independent_replay=len(unresolved), unresolved_pairs=unresolved,
             every_item_matrix_complete=False, final_mapper_releases_complete=False,
             exact_PPU_direct_captures=captures, references=references, rows=rows,
             driver_sha256=sha(Path(__file__)),
             scope='Single OJ hash only. Existing strict positive results are joined by identity/mode while every original negative attempt remains present, including later unsuccessful controller experiments for previously passing pairs. A failed controller is not automatically an engine defect. Earlier hashes and the unaccepted OV experiment do not count here. Old decoder PNG counts mean retained files; physical-frame timing is established only for the two listed direct captures. No every-item, exhaustive human visual, constant60Hz, full MMC3 or final-release claim.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    with (a.output / 'coverage.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['identity', 'mode', 'attempts', 'strict_independent_replay', 'direct_capture', 'every_item_verified'])
        for r in rows:
            key = r['identity'] + '-' + r['mode']
            writer.writerow([r['identity'], r['mode'], len(r['attempts']), r['strict_independent_replay'], key in captures, False])
    print(json.dumps({k: q[k] for k in ('ledger_complete', 'attempted_pairs', 'strict_independent_pairs', 'unresolved_pairs')}, indent=2))


if __name__ == '__main__':
    main()
