"""Bound a no-song-removal Parodius code/data placement proposal.

No source or allocation is applied. Reserved63/123/124/125/126/127 remain
reserved; any separate-E-mirror exchange needs independent proof/review.
"""
from pathlib import Path
import argparse, hashlib, json, random, re

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['gold', 'closure', 'legacy', 'layout', 'output']: p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    q = json.loads((a.gold / 'coverage.json').read_text())
    closure = json.loads((a.closure / 'coverage.json').read_text())
    old = json.loads((a.legacy / 'footprint.json').read_text())
    layout = json.loads(a.layout.read_text())
    assert q['passed'] and not q['unknown_pointer_origins']
    assert closure['passed'] and not closure['unknown_pointer_origins']
    assert closure['provenance_version'] == 3 and closure['first_exact_state_repeat_terminated_every_track']
    assert closure['reference_coverage_sha256'] == sha(a.gold / 'coverage.json')
    assert q['source_sha256'] == old['source_sha256']
    code = set()
    for row in q['source_instructions'].values(): code.update(range(row['physical'], row['physical'] + row['size']))
    data = set(q['ROM_data_reads'])
    readops = {'LDA', 'LDX', 'LDY', 'ADC', 'SBC', 'CMP', 'CPX', 'CPY', 'BIT', 'AND', 'ORA', 'EOR'}
    extra = set()
    for pc, values in q['accesses'].items():
        if q['source_instructions'][pc]['instruction'].split()[0] in readops:
            for at in values:
                if at >= 0x8000:
                    data.add(at + 0x10000)
                    if at + 0x10000 not in q['ROM_data_reads']: extra.add(at + 0x10000)
    actual_reads = {x for lo, hi in old['all_physical_read_ranges'] for x in range(lo, hi + 1)}
    assert not code & data
    assert not actual_reads - (code | data)
    assert not data - actual_reads
    assert data == set(closure['ROM_data_reads'])
    assert q['seen_instructions'] == closure['seen_instructions']
    # Keep the original multiplied header-base indexing as a real contiguous
    # source table; never forge a label before an allocation merely to match it.
    headers = set(range(0x18da5, 0x18da5 + 158 * 3))
    indexed_spans = set()
    for pc, values in q['accesses'].items():
        instruction = q['source_instructions'][pc]['instruction']
        match = re.fullmatch(r'(?:' + '|'.join(sorted(readops)) + r') \$([0-9a-fA-F]{4}),[XY]', instruction)
        if match:
            base = int(match[1], 16)
            for target in values:
                if base >= 0x8000 and target >= base:
                    indexed_spans.add((base, target))
    all_spans = {(base, target) for pc, pointer, base, target, delta in closure['final_pointer_plus_Y_accesses']}
    all_spans |= indexed_spans
    for pc, pointer, base, target, delta in closure['final_pointer_plus_Y_accesses']:
        assert delta == target - base and 0 <= delta <= 0xffff
    per_track = {}
    track_read_data_counts = {}
    padded_pointer_spans = set()
    for song, row in old['tracks'].items():
        reads = {x for lo, hi in row['physical_read_ranges'] for x in range(lo, hi + 1)}
        values = (reads & data) | headers
        track_read_data_counts[int(song)] = len(values)
        # A relocated pointer must retain every offset from its actual affine
        # base through its observed target. Include real intervening bytes,
        # rather than packing only the final read addresses. Using the global
        # pointer set per matching target deliberately over-approximates each
        # track; no track-specific pointer provenance is silently assumed.
        while True:
            before = len(values)
            for base, target in all_spans:
                if target + 0x10000 in values:
                    values.update(range(base + 0x10000, target + 0x10001))
                    padded_pointer_spans.add((base, target))
            if before == len(values): break
        per_track[int(song)] = values
    assert not (data | headers) - set.union(*per_track.values())
    slots = [(94, 0x300, 0x2000 - 0x300), (95, 0x400, 0x2000 - 0x400)]
    for bank, first, capacity in slots:
        assert any(g['bank'] == bank and not g['excluded'] and g['first'] <= first and g['end'] == 8192 for g in layout['gaps'])
    order = sorted(per_track, key=lambda s: -len(per_track[s]))
    rng = random.Random(20261025)
    solution, best_score = None, None
    feasible = 0
    for attempt in range(2000):
        if attempt: rng.shuffle(order)
        groups, unions = [[], []], [set(), set()]
        for song in order:
            options = [i for i, (_, _, capacity) in enumerate(slots) if len(unions[i] | per_track[song]) <= capacity]
            if not options: break
            choice = min(options, key=lambda i: (len(per_track[song] - unions[i]), len(unions[i])))
            groups[choice].append(song)
            unions[choice] |= per_track[song]
        else:
            feasible += 1
            # Choose the most balanced feasible result. A first-fit result
            # with a dozen bytes left would conceal useful layout uncertainty.
            slack = [cap - len(unions[i]) for i, (_, _, cap) in enumerate(slots)]
            score = (min(slack), sum(slack))
            if best_score is None or score > best_score:
                best_score = score
                solution = [dict(bank=bank, first=first, capacity=cap, songs=sorted(groups[i]),
                                 source_data_bytes=len(unions[i]), headroom_after_observed_pointer_spans=slack[i],
                                 physical_source_bytes=sorted(unions[i])) for i, (bank, first, cap) in enumerate(slots)]
    assert solution, 'Two chosen tails do not yet fit; retain failure before changing the plan.'
    report = dict(passed=True, feasibility_only=True, allocated_nothing=True, production_changes=False,
                  layout_ROM_sha256=layout['ROM_sha256'], source_ROM_sha256=q['source_sha256'],
                  source_code_bytes=len(code), source_load_only_data_field_bytes=len(q['ROM_data_reads']),
                  corrected_complete_ROM_data_bytes=len(data), additional_CMP_data_bytes=len(extra),
                  original_every_effective_read_accounted=True, original_actually_read_bytes=len(actual_reads),
                  conservatively_retained_code_operands_not_read=len(code - actual_reads),
                  contiguous_real_header_table_bytes=len(headers), header_prefix_extra_bytes=len(headers - data),
                  observed_pointer_spans_included=len(padded_pointer_spans),
                  direct_indexed_table_spans_included=len(indexed_spans),
                  final_indirect_pointer_plus_Y_bound=True,
                  pointer_closure_source_calls=closure['exact_reference_prefix_calls'],
                  pointer_closure_ordered_APU_stores=closure['exact_reference_prefix_APU_stores'],
                  unique_data_with_header_and_observed_pointer_spans=len(set.union(*per_track.values())),
                  track_sizes_with_pointer_spans={str(s): dict(before=track_read_data_counts[s], after=len(v)) for s, v in per_track.items()},
                  partition_attempts=2000, feasible_partitions=feasible, minimum_partition_headroom=best_score[0],
                  code_bank_proposal=dict(bank=62, first=0x300, capacity=0x1d00,
                                          requires_actual_assembled_relocation_fit=True),
                  data_bank_proposal=solution,
                  new_native_WRAM_proposal=dict(base=0x7400, source_RAM_bytes=256, source_ZP_bytes=17,
                                                source_RAM_ownership='Inactive XgLzHistory while native music owns the expanded decoder history',
                                                still_requires_complete_effective_access_and_interrupt_proof=True),
                  DMC=dict(source_span=[0xc040, 0xc540], bytes=1281,
                           separate_fixed_E_mirror_not_allocated=True,
                           cannot_keep_C_data_bank_only_during_audio_because_DMA_outlives_call=True,
                           reserved_TMNT63_124_and_shared125_preserved=True),
                  dispatch_proposal='Keep VgAudioDispatch23-byte resident C38 span. Character18 maps unified A62 selector; Parodius variants stay local; variant0 uses existing safe resident farcall tail to original Gradius. Preserve other routes and qualify actual stack/register/mapper/IRQ contracts.',
                  proof_dependencies={str(f): sha(f) for f in [a.gold / 'coverage.json', a.closure / 'coverage.json', a.legacy / 'footprint.json', a.layout]},
                  tool_sha256=sha(Path(__file__)), native_emulator_launched=False,
                  limits='Byte-set feasibility only, not a linked pointer layout. CMP-derived source tables and every observed affine base-to-target span are included in addition to load-derived provenance; a complete connected-pointer layout and any unobserved branch data remain to be assembled and qualified. Header copy is real allocated data. Source ROM/WRAM relocation, mirror, original SFX/requests, interrupts and no-harm native cadence remain open.')
    (a.output / 'proposal.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['data_bank_proposal', 'proof_dependencies']}, indent=2))
    print('DATA SLOTS', [{k: v for k, v in s.items() if k != 'physical_source_bytes'} for s in solution])


if __name__ == '__main__':
    main()
