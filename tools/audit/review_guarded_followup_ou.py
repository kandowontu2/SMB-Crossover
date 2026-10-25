"""Recheck the one Bass sample using its positively observed collision borrow."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('rom', 'evidence', 'baseline-review', 'guard', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    digest = sha(a.rom)
    prior = json.loads(a.baseline_review.read_text())
    assert prior['ROM_sha256'] == digest and len(prior['admitted']) == 4
    failures = prior['strict_review_failures']
    assert len(failures) == 1 and (failures[0]['identity'], failures[0]['mode']) == ('bass', 'easy')
    case = failures[0]['case']
    folder = Path(case['folder'])
    proof = json.loads((a.guard / 'proof.json').read_text())
    assert proof['passed'] and proof['ROM_sha256'] == digest and proof['observed']['repaired']
    for name in ('inputs.csv', 'trace.csv'):
        assert (a.guard / name).read_bytes() == (folder / name).read_bytes()
    rows = list(csv.DictReader((folder / 'trace.csv').open()))
    raw = {r['frame']: r for r in rows}
    borrowed = list(csv.DictReader((a.guard / 'borrowed-origin.csv').open()))
    assert len(borrowed) == 1 and borrowed[0]['frame'] == '3031'
    for event in borrowed:
        r = raw[event['frame']]
        assert event['blockAttack'] == '1'
        assert int(r['x']) == int(event['x']) == int(event['probeX'])
        assert int(r['y']) == int(event['y']) == int(event['probeY'])
        assert abs(int(event['savedX']) - int(event['lastDrawX'])) <= 8
        assert abs(int(event['savedY']) - int(event['lastDrawY'])) <= 8
        r['x'], r['y'] = event['savedX'], event['savedY']
    committed = [r for r in csv.DictReader((a.guard / 'committed-movement.csv').open())
                 if r['mode'] == '1' and r['task'] == '3' and r['engine'] == '8'
                 and r['world'] == r['level'] == '0']
    assert len(committed) > 1000 and all(r['blockAttack'] == '0' for r in committed)
    pairs = [(x, y) for x, y in zip(committed, committed[1:])
             if int(y['frame']) == int(x['frame']) + 1]
    assert len(pairs) > 500
    world = [abs(int(y['x']) - int(x['x'])) for x, y in pairs]
    camera = [int(y['camera']) - int(x['camera']) for x, y in pairs]
    assert max(world) <= 8 and min(camera) >= 0 and max(camera) <= 4
    original = ROOT / 'tools/audit/review_tmnt_ny.py'
    text = original.read_text()
    replacements = {
        "replay = json.loads((root / 'replay-results.json').read_text())": 'replay = explicit_replay',
        "len(replay['runs']) == 8": "len(replay['runs']) == 1",
        "trace = list(csv.DictReader((folder / 'trace.csv').open()))": 'trace = observed_player_rows',
        "overview_path = root / f'overview-{name}-{mode}.png'": "overview_path = review_root / f'overview-{name}-{mode}.png'",
        "(root / 'route-review.json').write_text": 'review_destination.write_text',
    }
    for before, after in replacements.items():
        assert text.count(before) == 1
        text = text.replace(before, after)
    destination = a.output / 'bass-easy.json'
    namespace = dict(__name__='observed_bass_borrow_review', __file__=str(original),
                     explicit_replay=dict(passed=True, ROM_sha256=digest, runs=[case]),
                     observed_player_rows=rows, review_root=a.output, review_destination=destination)
    exec(compile(text, str(original), 'exec'), namespace)
    sys.argv = [str(original), '--rom', str(a.rom), '--evidence', str(a.evidence)]
    namespace['main']()
    reviewed = json.loads(destination.read_text())
    assert reviewed['passed'] and set(reviewed['runs']) == {'bass-easy'}
    admitted = {**prior['admitted'], 'bass-easy': dict(review=str(destination), sha256=sha(destination),
                                                    result=reviewed['runs']['bass-easy'])}
    q = dict(passed=True, goal_complete=False, all_requested_routes_pass=False, ROM_sha256=digest,
             original_review=dict(path=str(a.baseline_review), sha256=sha(a.baseline_review), passed=prior['passed']),
             admitted=admitted, strict_review_failures=[], retained_negative_or_skipped=prior['retained_negative_or_skipped'],
             positive_observation=dict(guard_proof_sha256=sha(a.guard / 'proof.json'),
                                       borrowed_frames=[3031],
                                       borrowed_observer_sha256=sha(a.guard / 'borrowed-origin.csv'),
                                       committed_observer_sha256=sha(a.guard / 'committed-movement.csv'),
                                       completed_updates=len(committed), adjacent_pairs=len(pairs),
                                       max_world_step=max(world), max_camera_step=max(camera)),
             strict_reviewer_sha256=sha(original), adapter_sha256=sha(Path(__file__)),
             scope='The four existing strict results remain intact. Bass frame3031 is admitted only after a separate read-only replay positively observes the exact temporary block-probe coordinates and saved/drawn player origin, plus restored completed-loop motion. Original world<=8/camera<=4, exact replay, CHR and visible scanline31 bounds remain. Original negative reports and raw trace are unchanged. Old decoder PNG counts establish file retention, not exact physical-frame timing; direct captures are reviewed separately. Hard failures, full roster, every-item and release gates remain open.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print('PASS five follow-up route checks; Hard failures and capture-timing qualification retained')


if __name__ == '__main__':
    main()
