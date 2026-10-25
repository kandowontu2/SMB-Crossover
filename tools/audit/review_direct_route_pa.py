"""Apply unchanged route bounds to a verified direct physical-frame replay."""
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
    for name in ('rom', 'capture', 'discovery', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--guard', type=Path)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    digest = sha(a.rom)
    capture = json.loads((a.capture / 'proof.json').read_text())
    discovery = json.loads((a.discovery / 'manifest.json').read_text())
    assert capture['passed'] and capture['ROM_sha256'] == discovery['ROM_sha256'] == digest
    assert capture['source_discovery_manifest_sha256'] == sha(a.discovery / 'manifest.json')
    assert capture['fixed_inputs_and_trace_exact'] and capture['actual_PPU_frame_ids_complete']
    assert capture['every_saved_PNG_RGB_exact'] and capture['raw_gzip_roundtrip_exact']
    for name in ('inputs.csv', 'trace.csv'):
        assert (a.capture / name).read_bytes() == (a.discovery / name).read_bytes()
    assert capture['result'] == discovery['result'] and capture['result']['cleared'] and capture['result']['deaths'] == 0
    index = a.capture / 'direct-frame-index.csv'
    assert sha(index) == capture['frame_index_sha256']
    records = list(csv.DictReader(index.open()))
    assert [int(r['frame']) for r in records] == list(range(200, capture['result']['frames']))
    for r in records:
        assert r['frame'] == r['ppuFrame']
        assert sha(a.capture / 'frames' / f"{int(r['frame']):06d}.png") == r['PNG_sha256']
    rows = list(csv.DictReader((a.capture / 'trace.csv').open()))
    observation = None
    if a.guard:
        guard = json.loads((a.guard / 'proof.json').read_text())
        assert guard['passed'] and guard['ROM_sha256'] == digest and guard['observed']['repaired']
        for name in ('inputs.csv', 'trace.csv'):
            assert (a.guard / name).read_bytes() == (a.capture / name).read_bytes()
        raw = {r['frame']: r for r in rows}
        borrowed = list(csv.DictReader((a.guard / 'borrowed-origin.csv').open()))
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
        pairs = [(x, y) for x, y in zip(committed, committed[1:]) if int(y['frame']) == int(x['frame']) + 1]
        assert len(pairs) > 500
        world = [abs(int(y['x']) - int(x['x'])) for x, y in pairs]
        camera = [int(y['camera']) - int(x['camera']) for x, y in pairs]
        assert max(world) <= 8 and min(camera) >= 0 and max(camera) <= 4
        observation = dict(proof_sha256=sha(a.guard / 'proof.json'), borrowed_frames=[int(r['frame']) for r in borrowed],
                           max_committed_world_step=max(world), max_committed_camera_step=max(camera),
                           completed_updates=len(committed), adjacent_pairs=len(pairs),
                           borrowed_observer_sha256=sha(a.guard / 'borrowed-origin.csv'),
                           committed_observer_sha256=sha(a.guard / 'committed-movement.csv'))
    original = ROOT / 'tools/audit/review_tmnt_ny.py'
    source = original.read_text()
    replacements = {
        "replay = json.loads((root / 'replay-results.json').read_text())": 'replay = explicit_replay',
        "len(replay['runs']) == 8": "len(replay['runs']) == 1",
        "discovery = root / f'discover-{name}-{mode}-v1'": 'discovery = explicit_discovery',
        "manifest = json.loads((folder / 'manifest.json').read_text())": 'manifest = explicit_manifest',
        "trace = list(csv.DictReader((folder / 'trace.csv').open()))": 'trace = observed_player_rows',
        "overview_path = root / f'overview-{name}-{mode}.png'": "overview_path = review_root / f'overview-{name}-{mode}.png'",
        "(root / 'route-review.json').write_text": 'review_destination.write_text',
    }
    for before, after in replacements.items():
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    case = dict(identity=capture['identity'], mode=capture['mode'], folder=str(a.capture), frames=capture['result']['frames'])
    dest = a.output / 'route-review.json'
    namespace = dict(__name__='direct_replay_strict_review', __file__=str(original),
                     explicit_replay=dict(passed=True, ROM_sha256=digest, runs=[case]),
                     explicit_discovery=a.discovery, observed_player_rows=rows,
                     explicit_manifest=dict(ROM_sha256=digest, chr_commit=capture['body_chr']),
                     review_root=a.output, review_destination=dest)
    exec(compile(source, str(original), 'exec'), namespace)
    sys.argv = [str(original), '--rom', str(a.rom), '--evidence', str(a.capture.parent)]
    namespace['main']()
    strict = json.loads(dest.read_text())
    assert strict['passed'] and len(strict['runs']) == 1
    q = dict(passed=True, goal_complete=False, ROM_sha256=digest, identity=capture['identity'], mode=capture['mode'],
             strict_route=next(iter(strict['runs'].values())), positive_borrow_observation=observation,
             direct_capture_proof_sha256=sha(a.capture / 'proof.json'), direct_frame_index_sha256=sha(index),
             strict_review_sha256=sha(dest), original_reviewer_sha256=sha(original), adapter_sha256=sha(Path(__file__)),
             scope='Exact independent controller/trace replay, zero deaths and movable1-2; every retained PNG has verified direct physical PPU frame identity and matches its frame index hash. Original logical-world<=8, camera0..4, body-CHR and actual visible scanline31 bounds remain unchanged. Only positively observed source-owned temporary probe samples may use saved/drawn origins, with separate completed-loop motion bounds and raw traces untouched. Overview is sampled; exhaustive human visual, every-item, all-roster, 60Hz and final mapper gates remain open.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print('PASS strict direct replay', capture['identity'], capture['mode'])


if __name__ == '__main__':
    main()
