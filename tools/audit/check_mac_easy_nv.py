"""Independently bind Little Mac's NU controller clear to retained evidence."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'build/verification/mac-easy-nv'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--behavior', choices=['easy', 'hard'], default='easy')
    args = parser.parse_args(); hard = args.behavior == 'hard'
    manifest = QA / ('hard-manifest.json' if hard else 'manifest.json')
    assert sha(manifest) == ('2e5dbac790764e1cb3874c491b44c1bedbb82e13abbcafe2a52cae83460ea1d8' if hard else
                             '4f368aaa4cb75d64a653f79eee00643303a3a7678ca0e3d828dd73d971bb5d52')
    proof = json.loads(manifest.read_text())
    records = []
    def check(value):
        if isinstance(value, dict):
            if {'path', 'bytes', 'sha256'} <= value.keys():
                path = Path(value['path'])
                assert path.stat().st_size == value['bytes'], str(path)
                assert sha(path) == value['sha256'], str(path)
                records.append(str(path))
            for item in value.values(): check(item)
        elif isinstance(value, list):
            for item in value: check(item)
    check(proof)
    retained = 0
    for run in proof['runs'].values():
        inventory = json.loads(Path(run['all_files_inventory']['path']).read_text())
        folder = Path(inventory['folder']).parent
        for record in inventory['files']:
            path = folder / record['path']
            assert path.stat().st_size == record['bytes'] and sha(path) == record['sha256'], str(path)
            retained += 1
    discovery = proof['runs']['discover-hard-late8' if hard else 'discover-late8']
    replay = proof['runs']['replay-hard-late8' if hard else 'replay-late8']
    for key in ('inputs', 'trace'):
        assert Path(discovery[key]['path']).read_bytes() == Path(replay[key]['path']).read_bytes(), key
    rows = list(csv.DictReader(Path(replay['trace']['path']).open(newline='')))
    total, entry = (4023, 3999) if hard else (4933, 4909)
    assert len(rows) == total and int(rows[-1]['frame']) == total
    endpoint = [row for row in rows if int(row['frame']) >= entry]
    assert len(endpoint) == 25
    for row in endpoint:
        assert (int(row['world']), int(row['level']), int(row['area']), int(row['engine'])) == (0, 1, 192, 8)
        assert int(row['lives']) == 2
    assert int(endpoint[-1]['x']) > int(endpoint[0]['x'])
    for row in rows:
        if row['mode'] == '1' and row['task'] == '3':
            assert int(row['lives']) == 2, row
    report = dict(passed=True, source_manifest_sha256=sha(manifest), records_checked=len(records),
                  retained_files_checked=retained, full_input_and_trace_bytes_equal=True,
                  behavior=args.behavior, frames=len(rows), endpoint_control_frames=len(endpoint), ROM_SHA256=proof['ROM']['sha256'],
                  visual_review=('Root inspected the retained Hard route overview. Sampled review only.' if hard else
                                 'Root inspected the retained Easy route overview and pit comparison. Sampled review only.'),
                  scope=f'NU Little Mac {args.behavior} surface 1-1 to movable underground 1-2. No every-item, source audio or final-roster claim.')
    (QA / ('root-hard-review.json' if hard else 'root-review.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
