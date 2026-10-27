"""Review the bounded native shot journal; export only two whole-frame sheets."""
from pathlib import Path
import collections
import hashlib
import json
import sys

from final_inventory_compact_capture_v1 import records
from current_roster_compact_11_v1 import png


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    run = Path(sys.argv[1]).resolve()
    out = run / 'native'
    target = run / 'live-render-offline-review.json'
    assert not target.exists(), 'Preserve the previous review'
    ready = json.loads((run / 'prepared-not-run.json').read_text())
    assert sha(run / 'prepared-not-run.json') == sys.argv[2]
    for binding in ready['bindings']:
        assert sha(Path(binding['path'])) == binding['sha256'], binding['path']
    launch = json.loads((run / 'launch.json').read_text())
    result = json.loads((out / 'result.json').read_text())
    assert launch['exit_code'] == 0 and not launch['changed_inputs']
    assert launch['settings_before'] == launch['settings_after']
    assert result['passed'] and len(result['records']) == 53
    journal = [json.loads(line) for line in (out / 'live-render.jsonl').open()]
    draws = {q['draw']: q for q in journal if q['event'] == 'actual-shot-draw'}
    dmas = {q['epoch']: q for q in journal if q['event'] == 'actual-complete-DMA'}
    captures = [q for q in journal if q['event'] == 'captured-whole-PPU']
    terminal = journal[-1]
    assert terminal['event'] == 'passive-render-diagnostic-terminal'
    assert len(draws) == terminal['draws']
    assert len(captures) == terminal['whole_frames']
    assert [q['ordinal'] for q in captures] == list(range(1, len(captures) + 1))
    kinds = collections.Counter(q['kind'] for q in draws.values())
    assert set(kinds) == set(range(1, 14))
    spikes = [q for q in draws.values() if q['kind'] == 10]
    assert all(q['header'] == 0 and not q['writes'] for q in spikes)
    selected = {}
    for capture in captures:
        dma = dmas.get(capture.get('last_actual_DMA'))
        if not dma or not dma['full_completed_Main_source_match']:
            continue
        assert dma['source'] == dma['physical']
        for shot in dma['shots']:
            if not shot['source_written_bytes'] or not shot['all_written_bytes_retained']:
                continue
            draw = draws[shot['draw']]
            assert shot['kind'] == draw['kind'] and draw['header'] > 0
            kind = draw['kind']
            score = (abs(draw['age'] - 5), capture['ordinal'])
            if kind not in selected or score < selected[kind]['score']:
                selected[kind] = dict(score=score, capture=capture, dma_epoch=dma['epoch'],
                                      draw_id=draw['draw'], case_name=draw['name'],
                                      age=draw['age'], written_bytes=shot['source_written_bytes'])
    assert set(selected) == set(range(1, 14)) - {10}
    expected = [json.loads(line) for line in (out / 'captures-index.jsonl').open()]
    assert all(q['type'] == 'record' for q in expected)
    actual = []
    stream = hashlib.sha256()
    selected_raw = {}
    wanted = {q['capture']['ordinal'] for q in selected.values()}
    for meta, raw in records(out / 'captures.nesppuv1'):
        actual.append(meta)
        assert meta['kind'] == 1
        stream.update(raw)
        if meta['full_ordinal'] in wanted:
            selected_raw[meta['full_ordinal']] = raw
    assert actual == expected and len(actual) == len(captures)
    sheets = []
    ordered = sorted(selected)
    for offset in range(0, len(ordered), 6):
        subset = ordered[offset:offset + 6]
        path = run / ('live-weapons-sheet-%d.png' % (offset // 6 + 1))
        assert not path.exists()
        png(path, [selected_raw[selected[k]['capture']['ordinal']] for k in subset])
        sheets.append(dict(path=str(path), sha256=sha(path), placements=[
            dict(kind=k, row=i // 2, column=i % 2, **selected[k])
            for i, k in enumerate(subset)]))
    proof = dict(native_mechanics_pass=True, native_ROM_sha256=result['ROM_sha256'],
                 actual_draw_calls=len(draws), draws_per_kind=dict(kinds),
                 actual_full_PPU_frames=len(actual), decoded_stream_sha256=stream.hexdigest(),
                 selected_whole_frame_sheets=sheets, spikes_no_projectile_art=True,
                 agent_visual_review=False, all_frame_visual_review=False,
                 limits='Exact source-page content links completed Main and complete physical DMA; '
                 'identical repeated pages do not prove unique construction ownership. '
                 'Twelve selected full frames require separate human visual inspection. '
                 'Kind10 Spikes has native header0 and room-wide damage, with no shot art. '
                 'No all-frame, original-art, animation, shot-fairness, or audio verdict.',
                 bindings={str(out / n): sha(out / n) for n in
                           ['result.json', 'components.csv', 'live-render.jsonl',
                            'captures.nesppuv1', 'captures-index.jsonl']})
    target.write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(review=str(target), sha256=sha(target), draws=len(draws),
                          full_frames=len(actual), sheets=sheets), indent=2))


if __name__ == '__main__':
    main()
