"""Review actual bat draw/DMA captures, retaining three bounded whole-frame sheets."""
from pathlib import Path
import collections
import hashlib
import json
import sys

from final_inventory_compact_capture_v1 import records, verify
from current_roster_compact_11_v1 import png


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    run = Path(sys.argv[1]).resolve()
    ready_path = run / 'prepared-not-run.json'
    assert sha(ready_path) == sys.argv[2]
    ready = json.loads(ready_path.read_text())
    for binding in ready['bindings']:
        assert sha(Path(binding['path'])) == binding['sha256'], binding['path']
    launch = json.loads((run / 'launch.json').read_text())
    assert launch['exit_code'] == 0 and launch['changed_inputs'] == []
    assert launch['settings_before'] == launch['settings_after']
    native = run / 'native'
    result = json.loads((native / 'result.json').read_text())
    assert result['passed'] and len(result['records']) == 5
    assert result['ROM_sha256'] == ready['ROM_sha256'] == launch['ROM_sha256']
    journal = [json.loads(line) for line in (native / 'live-render.jsonl').open()]
    draws = {q['draw']: q for q in journal if q['event'] == 'actual-shot-draw'}
    dmas = {q['epoch']: q for q in journal if q['event'] == 'actual-complete-DMA'}
    captures = [q for q in journal if q['event'] == 'captured-whole-PPU']
    terminal = journal[-1]
    assert terminal['event'] == 'passive-render-diagnostic-terminal'
    assert len(draws) == terminal['draws'] == 60
    assert len(captures) == terminal['whole_frames'] == 180
    groups = collections.defaultdict(list)
    for d in draws.values():
        assert d['kind'] == 4 and d['record_bank'] == 97 and d['header'] == 4
        groups[d['name']].append(d['age'])
    assert len(groups) == 2 and all(v == list(range(1, 31)) for v in groups.values())
    committed = {}
    unmatched_capture_epochs = 0
    for capture in captures:
        dma = dmas.get(capture['last_actual_DMA'])
        if dma is None:
            unmatched_capture_epochs += 1
            continue
        if not dma['full_completed_Main_source_match']:
            continue
        assert dma['source'] == dma['physical']
        for shot in dma['shots']:
            if shot['source_written_bytes'] and shot['all_written_bytes_retained']:
                d = draws[shot['draw']]
                key = (d['name'], d['age'])
                if key not in committed:
                    committed[key] = dict(capture=capture, draw=d['draw'],
                                          age=d['age'], name=d['name'], record=d['record'])
    expected = {(name, age) for name in groups for age in range(1, 31)}
    assert set(committed) == expected, 'Every actual age must reach a captured committed DMA'
    # Every unique record per direction, not only a convenient late frame.
    selected, seen = [], set()
    for d in draws.values():
        key = (d['name'], d['record'])
        if key not in seen:
            selected.append(committed[(d['name'], d['age'])])
            seen.add(key)
    assert len(selected) == 20
    packed = verify(native / 'captures.nesppuv1', native / 'captures-index.jsonl')
    assert packed['full_frames'] == len(captures)
    wanted = {v['capture']['ordinal'] for v in selected}
    images = {}
    for meta, raw in records(native / 'captures.nesppuv1'):
        if meta['full_ordinal'] in wanted:
            images[meta['full_ordinal']] = raw
    sheets = []
    for start in range(0, len(selected), 8):
        subset = selected[start:start + 8]
        path = run / ('bat-live-shapes-%d.png' % (start // 8 + 1))
        assert not path.exists()
        png(path, [images[v['capture']['ordinal']] for v in subset])
        sheets.append(dict(path=str(path), sha256=sha(path),
                           placements=[dict(row=i // 2, column=i % 2, **v)
                                       for i, v in enumerate(subset)]))
    proof = dict(status='ACTUAL_BAT_CAPTURE_VERIFIED_VISUAL_REVIEW_PENDING',
                 native_ROM_sha256=result['ROM_sha256'], native_mechanics_pass=True,
                 actual_draws=60, both_directions_all30_ages_committed_and_captured=True,
                 unmatched_captured_DMA_epochs=unmatched_capture_epochs,
                 selected_unique_record_direction_pairs=20, sheets=sheets, container=packed,
                 terminal=terminal, root_visual_review=False, all_frame_visual_review=False,
                 limits='Content equality is not unique producer or opaque-pixel proof. '
                        'Selected twenty actual whole frames require human review. '
                        'Source/original palette fidelity and SMB spatial adaptations remain open.',
                 bindings={str(native / name): sha(native / name) for name in
                           ['result.json', 'components.csv', 'live-render.jsonl',
                            'captures.nesppuv1', 'captures-index.jsonl']}, goal_complete=False)
    target = run / 'bat-live-review.json'
    assert not target.exists()
    target.write_text(json.dumps(proof, indent=2) + '\n', newline='\n')
    print(json.dumps(dict(review=str(target), draws=60, selected=20,
                          sheets=[v['path'] for v in sheets])))


if __name__ == '__main__':
    main()
