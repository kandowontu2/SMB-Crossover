"""Verify bounded live Kirby captures and prepare one selected whole-frame sheet."""
from pathlib import Path
import argparse
import collections
import hashlib
import json

from final_inventory_compact_capture_v1 import records, verify
from current_roster_compact_11_v1 import png


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ready', type=Path, required=True)
    parser.add_argument('--expected-ready', required=True)
    parser.add_argument('--ordinals', required=True)
    args = parser.parse_args()
    ready = args.ready.resolve()
    assert sha(ready) == args.expected_ready
    q = json.loads(ready.read_text())
    for binding in q['bindings']:
        assert sha(Path(binding['path'])) == binding['sha256'], binding['path']
    directory = ready.parent
    native = directory / 'native'
    target = directory / 'live-review.json'
    sheet = directory / 'selected-live-whole-frames.png'
    assert not target.exists() and not sheet.exists()
    launch = json.loads((directory / 'launch.json').read_text())
    assert launch['exit_code'] == 0 and launch['changed_inputs'] == []
    assert launch['ready_sha256'] == args.expected_ready
    assert launch['settings_before'] == launch['settings_after']
    result = json.loads((native / 'result.json').read_text())
    assert result['passed'] and result['native_run']
    assert result['ROM_sha256'] == q['ROM_sha256'] == launch['ROM_sha256']
    events = [json.loads(line) for line in (native / 'live-render.jsonl').open()]
    terminal = events[-1]
    assert terminal['event'] == 'passive-live-terminal'
    captures = [v for v in events if v['event'] == 'captured-whole-PPU']
    assert [v['ordinal'] for v in captures] == list(range(1, len(captures) + 1))
    assert len(captures) == terminal['whole_frames']
    container = native / 'captures.nesppuv1'
    index = native / 'captures-index.jsonl'
    packed = verify(container, index)
    assert packed['full_frames'] == len(captures) == terminal['capture']['full_frames']
    assert container.stat().st_size <= 134217728 and packed['physical_records'] <= 3000
    wanted = [int(v) for v in args.ordinals.split(',')]
    assert 0 < len(wanted) <= 8 and len(set(wanted)) == len(wanted)
    assert all(1 <= v <= len(captures) for v in wanted)
    images = {}
    for record, raw in records(container):
        ordinal = record['full_ordinal']
        assert record['kind'] == 1
        observed = captures[ordinal - 1]
        assert record['stamp']['actual_DMA'] == observed['actual_DMA']
        assert record['stamp']['case'] == observed['case']
        assert record['stamp']['ppu'] == observed['stamp']
        if ordinal in wanted:
            images[ordinal] = raw
    png(sheet, [images[v] for v in wanted])
    coverage = collections.defaultdict(collections.Counter)
    for v in captures:
        coverage[v['name']][v['phase']] += 1
    proof = {
        'status': 'CAPTURES_VERIFIED_SELECTED_IMAGES_PREPARED_NOT_VISUALLY_REVIEWED',
        'actual_ROM_sha256': result['ROM_sha256'],
        'unit': result['unit'],
        'mechanics_native_passed': True,
        'ready_sha256': args.expected_ready,
        'container': packed,
        'terminal': terminal,
        'capture_coverage': {k: dict(v) for k, v in coverage.items()},
        'captured_physical_OAM_matches_DMA': sum(v['physical_OAM_matches_DMA'] for v in captures),
        'selected_whole_frames': [dict(ordinal=v, row=i // 2, column=i % 2,
                                      native=captures[v - 1], raw_sha256=sha_raw(images[v]))
                                  for i, v in enumerate(wanted)],
        'sheet': {'path': str(sheet), 'sha256': sha(sheet)},
        'files': {p.name: sha(p) for p in [native / 'result.json', native / 'live-render.jsonl',
                                         directory / 'launch.json', ready]},
        'root_visual_review': False,
        'all_frame_visual_review': False,
        'limits': 'Physical/source equality is content linkage, not a unique producer or visibility verdict. '
                  'Duplicate/unmatched/carry provenance remains in terminal totals. '
                  'Selected actual pixels require human review; source art IDs do not prove appearance.',
        'goal_complete': False,
    }
    target.write_text(json.dumps(proof, indent=2) + '\n', newline='\n')
    print(json.dumps({'proof': str(target), 'full_frames': len(captures),
                      'selected': wanted, 'sheet': str(sheet)}))


def sha_raw(raw):
    return hashlib.sha256(raw).hexdigest()


if __name__ == '__main__':
    main()
