"""Freeze one failed Easy parser pilot without masking cadence/prefix deficits."""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import gzip
import json
import math
import shutil
import statistics
from tmnt_native_storage_driver import ROOT, CURRENT, OB, sha
from tmnt_native_storage_cpu import Probe


def rows(path):
    with path.open() as stream: return list(csv.DictReader(stream))


def stats(values):
    values = sorted(values)
    assert values
    return dict(count=len(values), mean=statistics.mean(values), p95_nearest_rank=values[math.ceil(.95 * len(values)) - 1], maximum=max(values))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    d, out = a.experiment, a.output
    pair = d / 'parser-native-pilot-v1'
    assert not out.exists() and not out.resolve().is_relative_to(ROOT)
    strict = json.loads((pair / 'easy-strict-proof.json').read_text())
    assert strict['measurement_valid'] and not strict['performance_gate_passed']
    assert strict['baseline_ROM_sha256'] == CURRENT
    assert strict['candidate_ROM_sha256'] == '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
    assert strict['behavior'] == 0
    folders = {label: pair / (label + '-easy') for label in ['baseline', 'candidate']}
    native = {label: json.loads((folder / 'native-result.json').read_text()) for label, folder in folders.items()}
    assert all(j['passed'] and j['mode-readback.json']['actual'] == j['mode-readback.json']['requested'] == 0 for j in native.values())
    assert native['baseline']['dependencies'] == native['candidate']['dependencies']
    boundary = {}
    for label, folder in folders.items():
        records = [json.loads(line) for line in (folder / 'before-phase-setup.jsonl').read_text().splitlines()]
        assert len(records) == 10
        staged = [r for r in records if r['kind'] == 'staged']
        assert len(staged) == 5
        commands = []
        for record in staged:
            writes = record['writes']
            if isinstance(writes, dict): writes = [writes[k] for k in sorted(writes, key=int)]
            assert writes
            assert all(0 <= row['address'] < 0x8000 and not 0x2000 <= row['address'] < 0x5c00 and not 0x7400 <= row['address'] < 0x7500 for row in writes)
            commands.append(dict(phase=record['data']['phase'], step=record['data']['step'],
                                 writes=[{name: row[name] for name in ['address', 'value', 'name']} for row in writes]))
        boundary[label] = commands
    assert boundary['baseline'] == boundary['candidate']
    # Compare actual executed source requests and full state to the original,
    # retaining only the existing proven ROM-word high-byte relocation.
    states, requests = rows(folders['candidate'] / 'source-state.csv'), rows(folders['candidate'] / 'source-apu.csv')
    assert len(states) == 602 and len(requests) == 2125
    gold = json.loads(gzip.decompress((OB / 'probe-v2/song-02.json.gz').read_bytes()))
    original = Probe(d / 'standalone-original-v1', True)
    positions = list(range(0xe0, 0xee)) + list(range(0x7000, 0x70ae))
    grouped = defaultdict(list)
    for row in requests: grouped[int(row['serial'])].append([int(row['register']), int(row['value'])])
    for tick, row in enumerate(states):
        assert int(row['serial']) == tick + 1 and int(row['sourceTick']) == tick and int(row['song']) == 2
        original.call(gold[tick], 2)
        expected = bytes((original.m[at] - (27 if original.origin.get(at) in original.changed_high else 0)) & 255 for at in positions)
        assert bytes.fromhex(row['ZP14_RAM174_hex']) == expected
        assert grouped[tick + 1] == gold[tick]['writes']
    baseline_replay = {name: sha(folders['baseline'] / name) == sha(d / 'native-pilots-v1/diagnostic-baseline-easy-v2' / name)
                       for name in ['gameplay.csv', 'tmnt-performance-calls.csv', 'tmnt-performance-frames.csv']}
    assert all(baseline_replay.values())
    source_state_matches_frozen_a983 = sha(folders['candidate'] / 'source-state.csv') == sha(d / 'native-pilots-v1/diagnostic-candidate-easy-v3/source-state.csv')
    assert source_state_matches_frozen_a983
    ledgers = {label: [json.loads(line) for line in (folder / 'native-bus.jsonl').read_text().splitlines()] for label, folder in folders.items()}
    audio = {label: rows(folder / 'audio-components.csv') for label, folder in folders.items()}
    phase_costs, components = {}, {}
    for label, folder in folders.items():
        main = rows(folder / 'tmnt-performance-calls.csv')
        phase_costs[label] = {}
        for phase in ['idle', 'walk', 'enemies', 'primary', 'secondary']:
            top = [r for r in audio[label] if r['name'] == 'AudioUpdate' and r['phase'] == phase]
            loop = [r for r in main if r['name'] == 'GameLoop' and r['phase'] == phase]
            phase_costs[label][phase] = dict(AudioUpdate_including_IRQ=stats([int(r['inclusiveCycles']) for r in top]),
                                           AudioUpdate_excluding_IRQ=stats([int(r['CPUcycles']) for r in top]),
                                           GameLoop_foreground_excluding_NMI_IRQ=stats([int(r['cpuCycles']) for r in loop]))
        for top in [r for r in audio[label] if r['name'] == 'AudioUpdate']:
            nested = [r for r in audio[label] if int(r['startCPU']) >= int(top['startCPU']) and int(r['endCPU']) <= int(top['endCPU'])]
            assert sum(int(r['exclusiveCPUcycles']) for r in nested) == int(top['CPUcycles'])
        grouped_components = defaultdict(list)
        for r in audio[label]: grouped_components[r['phase'], r['name']].append(int(r['exclusiveCPUcycles']))
        components[label] = {phase: {name: stats(value) for (tag, name), value in grouped_components.items() if tag == phase}
                             for phase in ['idle', 'walk', 'enemies', 'primary', 'secondary']}
    first = strict['all_completed_update_prefix_deficits'][0]
    first_index = first['update']
    window = {}
    for label in ['baseline', 'candidate']:
        draw = next(r for r in ledgers[label] if r['kind'] == 'draw-construction' and r['index'] == first_index)
        complete = next(r for r in ledgers[label] if r['kind'] == 'completed-game-update' and r['index'] == first_index)
        top = max((r for r in audio[label] if r['name'] == 'AudioUpdate' and int(r['endCPU']) <= draw['stamp']['cpu']), key=lambda r: int(r['endCPU']))
        nested = [r for r in audio[label] if int(r['startCPU']) >= int(top['startCPU']) and int(r['endCPU']) <= int(top['endCPU'])]
        window[label] = dict(draw=draw, complete=complete, preceding_AudioUpdate=top, disjoint_components=nested)
    assert first_index == 406
    assert window['baseline']['draw']['stamp']['frame'] == window['baseline']['complete']['stamp']['frame'] == 735
    assert window['candidate']['draw']['stamp']['frame'] == 735 and window['candidate']['complete']['stamp']['frame'] == 736
    source_tick = next(int(row['sourceTick']) for row in requests if int(window['candidate']['preceding_AudioUpdate']['startCPU']) <= int(row['cpu']) <= int(window['candidate']['preceding_AudioUpdate']['endCPU']))
    assert source_tick == 407
    draw_delta = window['candidate']['draw']['stamp']['cpu'] - window['baseline']['draw']['stamp']['cpu']
    audio_end_delta = int(window['candidate']['preceding_AudioUpdate']['endCPU']) - int(window['baseline']['preceding_AudioUpdate']['endCPU'])
    dmc = {label: rows(folder / 'dmc-instruction-clocks.csv') for label, folder in folders.items()}
    dmc_summary = {label: dict(samples=len(value), actual_instruction_cycles=dict(Counter(r['actualCPUcycles'] for r in value)), extra_cycles=dict(Counter(r['extraCycles'] for r in value))) for label, value in dmc.items()}
    details = dict(source_state_original_calls=602, original_ordered_APU=2125,
                   actual_source_state_stream_byte_exact_frozen_a983=source_state_matches_frozen_a983,
                   baseline_replay_CSVs_byte_exact=baseline_replay, exact_before_phase_setup_commands=True,
                   actual_mode_readbacks={label: report['mode-readback.json'] for label, report in native.items()},
                   phase_costs=phase_costs, disjoint_exclusive_components=components,
                   first_prefix_deficit=first, first_causal_deadline=window, source_tick_first_miss=source_tick,
                   draw_start_CPU_delay=draw_delta, preceding_AudioUpdate_return_CPU_delay=audio_end_delta,
                   residual_post_audio_foreground_delay=draw_delta-audio_end_delta,
                   direct_DMC_STA_instruction_clocks=dmc_summary,
                   limits='Residual read-halt/DMA attribution is not claimed complete; direct STA clocks are separate. No additional native case/retry/Hard or acceptance.')
    out.mkdir(parents=True)
    (out / 'diagnosis.json').write_text(json.dumps(details, indent=2) + '\n')
    shutil.copyfile(pair / 'easy-strict-proof.json', out / 'easy-strict-proof.json')
    tools = {}; (out / 'tools').mkdir()
    for name in ['tmnt_native_storage_parser_native.py', 'tmnt_native_storage_parser_native_report.py', 'tmnt_native_storage_native_compare.py']:
        path = ROOT / 'tools/audit' / name;shutil.copyfile(path, out / 'tools' / name);tools[name] = sha(path)
    artifacts = {str(path): sha(path) for folder in folders.values() for path in folder.iterdir() if path.is_file()}
    report = f'''TMNT parser9a791: SINGLE EASY NATIVE PERFORMANCE GATE FAILED
No adoption. One sequential native grant RELEASED after this pair. No retries,
Hard, campaign, rate/state/store changes or within-phase outcome injection.

Baseline {CURRENT}
Candidate {strict['candidate_ROM_sha256']}
Raw pair {pair}

Both real cold numericEasy0 runs complete600updates and all original
source/hardware/DMC/mixed4015/NMI/IRQ/5SMC/stack/bank/CHR/complete256B-DMA
guards pass. Baseline572 completedDMA versus candidate566; every destination
byte matches the entire source page inside vblank/disabled rendering.
Both have921 observedNMIs/maxdepth1 and600activeIRQs. Candidate602source calls,
2125orderedAPUs,8400hardware comparisons,54activeDMC/540heldDAC44frames.
Fresh original executable comparison preserves every188B source state using
only original-ROM-word pointer translation, and all602APU streams. Actual
source-state CSV is byte-exact to priora983. Baseline gameplay/call/frame CSVs
are byte-exact to its historical frozen control. All five BEFORE setup command
lists are equal, actual stage/ground/actor guards pass; no natural gear claim.

STRICT NEGATIVE
Idle/walk/enemies0 added skips. Primary0->1 skipped draw and longeststall0->1.
Secondary28->33 skipped draws; longeststall1unchanged. Six added lost draws,
down from priora983eight but still a failure. All195absolute/144phase prefix
deficits retained. Two input-only differences at532/560; every other recorded
game field matches. Equal929totalframes does not override lost draws.

FIRST CAUSAL DEADLINE
Update406 baseline drawPPU735 scan162/dot317 and complete735 scan218/dot295;
candidate draw735 scan188/dot160 and complete736 scan7/dot295 across realNMI.
Update407 then uses the actual no-draw catch-up return. Draw starts{draw_delta}
CPUcycles later; precedingAudioUpdate returns{audio_end_delta}cycles later,
leaving{draw_delta-audio_end_delta}cycles of measured postaudio foreground residual.
The preceding original music burst is actualsourceTick407, with matching
captured source state and unchanged requested APUs. diagnosis.json records
actual complete AudioUpdate/core/writer/adapter/mixer/IRQ intervals and disjoint
exclusive costs, plus per-phase mean/P95/max AudioUpdate and foreground.
The known isolatedCPU398saved at407 versus a983 does not imply native success.
Direct DMC STA clocks remain separated from subsequent read-halt DMA residuals;
no unsupported full-DMA attribution or native60Hz claim.

Source-only parser and multiply ready packets and all earlier negative trials
remain immutable. This native negative is a hold, not an accepted music build.
No production, Git, Downloads or guide/video updates were made.
'''
    (out / 'report.txt').write_text(report)
    receipt = dict(frozen=True, accepted=False, performance_gate_passed=False, source_hardware_guard_passed=True,
                   native_scope='single fresh Easy600 same-work pair only', grant_released=True,
                   baseline_ROM_sha256=CURRENT, candidate_ROM_sha256=strict['candidate_ROM_sha256'],
                   raw_pair=str(pair), added_skipped_draws=6, absolute_prefix_deficits=195, phase_prefix_deficits=144,
                   original_source_calls=602, original_APU=2125, original_source188state_exact=True,
                   baseline_historical_CSVs_exact=True, same_BEFORE_setup_commands=True,
                   first_miss_source_tick=407, draw_start_delay_CPUcycles=draw_delta, postaudio_residual_CPUcycles=draw_delta-audio_end_delta,
                   tools=tools, artifacts=artifacts, report_sha256=sha(out / 'report.txt'),
                   strict_sha256=sha(out / 'easy-strict-proof.json'), diagnosis_sha256=sha(out / 'diagnosis.json'))
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(frozen=True, accepted=False, receipt_sha256=sha(out / 'receipt.json'),
                          source_calls=602, source_APU=2125, draw_delay=draw_delta, postaudio_residual=draw_delta-audio_end_delta)))


if __name__ == '__main__':
    main()
