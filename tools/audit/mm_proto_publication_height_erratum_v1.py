"""Additive, offline correction of a801's eight-high first-eight derivation."""
from pathlib import Path
import argparse
import bisect
import collections
import hashlib
import json

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
N = D / 'mm-proto-publication-native-ready-v1'
R = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get(path):
    return json.loads(Path(path).read_text())


def put(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def raw(value):
    if isinstance(value, dict):
        return bytes(value[str(i)] for i in range(1, 257))
    return bytes(value)


def first_eight(data, indices, height):
    rejected = []
    selected = []
    for y in range(240):
        # These actual owned records are below the top edge. This is the
        # visible-Y rectangle model, not opaque pixels or a PPU emulator.
        candidates = [i for i in range(64)
                      if data[i * 4] < 240 and data[i * 4] < y <= data[i * 4] + height]
        live = set(candidates[:8])
        demand = set(candidates) & indices
        if demand - live:
            rejected.append(dict(y=y, indices=sorted(demand - live)))
        if demand & live:
            selected.append(y)
    return dict(rejected_scanlines=len(rejected),
                rejected_record_scanlines=sum(len(q['indices']) for q in rejected),
                first_rejections=rejected[:4], selected_scanlines=len(selected))


def runs(frames):
    answer = []
    for frame in frames:
        if answer and answer[-1][-1] + 1 == frame:
            answer[-1].append(frame)
        else:
            answer.append([frame])
    return answer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    old_rows_path = N / 'review-v2/actual-owned-publications.json'
    old_proof_path = N / 'review-v2/proof.json'
    old_pairs_path = N / 'review-v2/all275-pairs.json'
    old_runs_path = N / 'freeze-v1/actual-visible-first8-record-runs.json'
    old_rows = get(old_rows_path)
    old_proof = get(old_proof_path)
    old_pairs = get(old_pairs_path)
    assert old_proof['candidate_ROM_sha256'] == 'a801f8e397a416e1b12cb6b78bad25774670c8f9fea0e8334cd0c830cf8a3d56'
    assert old_proof['physical_DMA_net_delta'] == -3
    assert old_proof['release_suitable'] is False
    logs = [json.loads(line) for line in (N / 'timing.jsonl').read_text().splitlines()]
    dmas = [q['DMA'] for q in logs if q['kind'] == 'DMA-complete']
    assert len(dmas) == 399
    assert [q['id'] for q in dmas] == list(range(1, 400))
    for q in dmas:
        assert q['completed_writes'] == 256
        assert raw(q['source']) == raw(q['hardware'])
    owners = [json.loads(line) for line in (N / 'ownership.jsonl').read_text().splitlines()]
    by_id = {q['DMA']['id']: q['DMA'] for q in owners if q['kind'] == 'DMA-source-owner'}
    corrected = []
    for old in old_rows:
        dma = dmas[old['DMA'] - 1]
        owner = by_id[old['DMA']]
        assert raw(dma['source']) == raw(owner['source']) == raw(owner['last_roster']['source'])
        height = 16 if dma['ctrl'] & 0x20 else 8
        data = raw(dma['hardware'])
        body_indices = set(range(old['body_start'] // 4, (old['body_start'] + old['B']) // 4))
        shot_indices = set(range(old['shot_start'] // 4, (old['shot_start'] + old['S']) // 4))
        # Reproduce the historical mistake exactly before replacing the
        # derived numbers. Never edit the original proof or raw evidence.
        assert first_eight(data, body_indices, 8) == old['body_first8']
        assert first_eight(data, shot_indices, 8) == old['shots_first8']
        row = dict(old)
        row.update(captured_PPUCTRL=dma['ctrl'], sprite_height=height,
                   body_first8=first_eight(data, body_indices, height),
                   shots_first8=first_eight(data, shot_indices, height))
        corrected.append(row)
    assert len(corrected) == 46
    assert [q['phase'] for q in corrected] == ['body', 'shots'] * 23
    by_corrected = {q['DMA']: q for q in corrected}
    frame_rows = []
    for pair in old_pairs:
        count = pair['candidate_completed_DMA']
        row = by_corrected.get(count)
        frame_rows.append(dict(frame=pair['frame'], last_DMA=count,
                               derived_owned_source_available=row is not None,
                               body_record_rejected=bool(row and row['body_first8']['rejected_scanlines']),
                               shot_record_rejected=bool(row and row['shots_first8']['rejected_scanlines'])))
    # Prove these are the same visible capture cutoffs, rather than a new
    # source-frame approximation. The old file's result is withdrawn only
    # for its first-eight geometry, not its timing or image selection.
    old_by_id = {q['DMA']: q for q in old_rows}
    old_rejected_frames = [q['frame'] for q in old_pairs
                           if q['candidate_completed_DMA'] in old_by_id
                           and old_by_id[q['candidate_completed_DMA']]['body_first8']['rejected_scanlines']]
    assert runs(old_rejected_frames) == get(old_runs_path)['body_record_rejection_runs']
    counts = {}
    for phase in ['body', 'shots']:
        for role in ['body', 'shots']:
            key = phase + '_turns_with_any_' + role + '_record_rejection'
            counts[key] = sum(q['phase'] == phase and bool(q[role + '_first8']['rejected_scanlines'])
                              for q in corrected)
    visible_runs = {}
    for role in ['body', 'shot']:
        rr = runs([q['frame'] for q in frame_rows if q[role + '_record_rejected']])
        visible_runs[role + '_record_rejection_runs'] = rr
        visible_runs[role + '_max_visible_frame_run'] = max(map(len, rr), default=0)
    # One finite geometry check: eight earlier 16-high rectangles consume
    # scanline 20 even when their bottom CHR halves might be transparent.
    test = bytearray([248, 0, 0, 0] * 64)
    for slot in range(9):
        test[4 * slot] = 9
    assert first_eight(test, {8}, 8)['rejected_scanlines'] == 8
    assert first_eight(test, {8}, 16)['rejected_scanlines'] == 16
    put(args.output / 'corrected-owned-publications.json', corrected)
    put(args.output / 'corrected-visible-record-runs.json', visible_runs)
    put(args.output / 'corrected-visible-frame-links.json', frame_rows)
    summary = dict(passed=True, additive_erratum=True, native_run=False,
                   original_frozen_reports_unchanged=True, original_eight_high_counts_withdrawn=True,
                   candidate_ROM_sha256=old_proof['candidate_ROM_sha256'],
                   full_source_hardware_256_checks=399, owned_publications=46,
                   captured_PPUCTRL_counts=dict(collections.Counter(str(q['captured_PPUCTRL']) for q in corrected)),
                   actual_height_counts=dict(collections.Counter(str(q['sprite_height']) for q in corrected)),
                   corrected_rejection_counts=counts,
                   corrected_visible_runs=visible_runs,
                   unchanged_native_phase_turns_each=23, unchanged_physical_DMA_net_delta=-3,
                   unchanged_source_Vine_body_overwrite_cases=3, release_suitable=False,
                   opaque_pixel_attribution_proved=False,
                   scope='Correct actual 8x16 rectangle selection only, using each captured DMA PPUCTRL. No alpha/CHR/palette attribution, new native work, state change, equality mask, or acceptance. Transparent halves still consume first-eight selection. Original full DMA, actual image pixels, source/ack phases, cadence failure and Vine counterexample are unchanged.',
                   tool_sha256=sha(__file__))
    put(args.output / 'proof.json', summary)
    dependencies = [Path(__file__), old_rows_path, old_proof_path, old_pairs_path,
                    old_runs_path, N / 'timing.jsonl', N / 'ownership.jsonl',
                    R / 'tools/audit/mm_proto_priority450_review_v1.py',
                    R / 'tools/audit/mm_proto_publication_native_review_v2.py',
                    R / 'tools/audit/mm_proto_postdma_native_review_v3.py']
    put(args.output / 'bindings.json', {str(p.resolve()): sha(p) for p in dependencies})
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
