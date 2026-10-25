"""Freeze the failed native Easy gate and its exact same-work diagnostic pair."""
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
    assert not out.resolve().is_relative_to(ROOT)
    pilots = d / 'native-pilots-v1'
    labels = ['baseline-easy', 'candidate-easy', 'diagnostic-baseline-easy-v2', 'diagnostic-candidate-easy-v3']
    results = {label: json.loads((pilots / label / 'native-result.json').read_text()) for label in labels}
    assert all(result['passed'] for result in results.values())
    strict = json.loads((pilots / 'easy-strict-proof.json').read_text())
    assert strict['measurement_valid'] and not strict['performance_gate_passed']
    assert strict['phases']['primary']['added_lag_NMIs'] == 2 and strict['phases']['secondary']['added_lag_NMIs'] == 6
    replay = {}
    for initial, diagnostic in zip(labels[:2], labels[2:]):
        replay[initial] = {name: sha(pilots / initial / name) == sha(pilots / diagnostic / name)
                           for name in ['gameplay.csv', 'tmnt-performance-frames.csv', 'tmnt-performance-calls.csv']}
        assert all(replay[initial].values())
    diagnostic = pilots / labels[3]
    states = rows(diagnostic / 'source-state.csv')
    requests = rows(diagnostic / 'source-apu.csv')
    assert len(states) == 602 and len(requests) == 2125
    gold = json.loads(gzip.decompress((OB / 'probe-v2/song-02.json.gz').read_bytes()))
    source = Probe(d / 'standalone-original-v1', True)
    positions = list(range(0xe0, 0xee)) + list(range(0x7000, 0x70ae))
    grouped = defaultdict(list)
    for row in requests: grouped[int(row['serial'])].append([int(row['register']), int(row['value'])])
    for index, row in enumerate(states):
        assert int(row['serial']) == index + 1 and int(row['sourceTick']) == index and int(row['song']) == 2
        source.call(gold[index], 2)
        expected = bytes((source.m[at] - (27 if source.origin.get(at) in source.changed_high else 0)) & 255 for at in positions)
        assert expected == bytes.fromhex(row['ZP14_RAM174_hex']), ('Actual native source-state divergence', index)
        assert grouped[index + 1] == gold[index]['writes'], ('Actual native original ordered requests', index)
    audio = {label: rows(pilots / label / 'audio-components.csv') for label in labels[2:]}
    cost = {}
    for label in labels[2:]:
        entry = {}
        main = rows(pilots / label / 'tmnt-performance-calls.csv')
        for phase in ['idle', 'walk', 'enemies', 'primary', 'secondary']:
            top = [row for row in audio[label] if row['name'] == 'AudioUpdate' and row['phase'] == phase]
            calls = [row for row in main if row['name'] == 'GameLoop' and row['phase'] == phase]
            entry[phase] = dict(AudioUpdate_including_nested_IRQ=stats([int(row['inclusiveCycles']) for row in top]),
                                AudioUpdate_excluding_IRQ=stats([int(row['CPUcycles']) for row in top]),
                                GameLoop_foreground_excluding_NMI_IRQ=stats([int(row['cpuCycles']) for row in calls]))
        cost[label] = entry
        for top in [row for row in audio[label] if row['name'] == 'AudioUpdate']:
            children = [row for row in audio[label] if int(row['startCPU']) >= int(top['startCPU']) and int(row['endCPU']) <= int(top['endCPU'])]
            assert sum(int(row['exclusiveCPUcycles']) for row in children) == int(top['CPUcycles']), ('Disjoint CPU accounting', label, top['serial'])
    by_phase_components = {}
    for phase in ['idle', 'walk', 'enemies', 'primary', 'secondary']:
        components = defaultdict(list)
        for row in audio[labels[3]]:
            if row['phase'] == phase: components[row['name']].append(int(row['exclusiveCPUcycles']))
        by_phase_components[phase] = {name: stats(values) for name, values in components.items()}
    window, peak = {}, {}
    for label in labels[2:]:
        top = next(row for row in audio[label] if row['name'] == 'AudioUpdate' and int(row['startFrame']) == 735)
        children = [row for row in audio[label] if int(row['startCPU']) >= int(top['startCPU']) and int(row['endCPU']) <= int(top['endCPU'])]
        window[label] = dict(AudioUpdate=top, disjoint_children=children)
        peak[label] = max((row for row in audio[label] if row['name'] == 'AudioUpdate'), key=lambda row: int(row['CPUcycles']))
    assert int(window[labels[2]]['AudioUpdate']['inclusiveCycles']) == 3014
    assert int(window[labels[3]]['AudioUpdate']['inclusiveCycles']) == 6283
    # The recorded direct DMC STA instruction has its ordinary four-cycle
    # clock span. Subsequent read-halt DMA costs are not relabeled STA costs.
    dmc = {label: rows(pilots / label / 'dmc-instruction-clocks.csv') for label in labels[2:]}
    dmc_summary = {label: dict(samples=len(value), actual_instruction_cycles=dict(Counter(row['actualCPUcycles'] for row in value)),
                               additional_clock_cycles=dict(Counter(row['extraCycles'] for row in value))) for label, value in dmc.items()}
    source_tick = next(int(row['sourceTick']) for row in requests if int(window[labels[3]]['AudioUpdate']['startCPU']) <= int(row['cpu']) <= int(window[labels[3]]['AudioUpdate']['endCPU']))
    assert source_tick == 407
    frozen = json.loads((d / 'current-baseline-v1/frozen-source.json').read_text())
    assert all(sha(ROOT / name) == value for name, value in frozen['source_files'].items())
    out.mkdir(parents=True, exist_ok=False)
    details = dict(costs=cost, disjoint_exclusive_components=by_phase_components, first_miss_window=window,
                   maximum_AudioUpdate=peak, source_tick_first_miss=source_tick, direct_DMC_STA_clocks=dmc_summary,
                   actual_native_source_state188_exact_calls=len(states), actual_native_original_requests=len(requests),
                   diagnostic_replays_byte_exact_initial=replay)
    (out / 'diagnosis.json').write_text(json.dumps(details, indent=2) + '\n')
    shutil.copyfile(pilots / 'easy-strict-proof.json', out / 'easy-strict-proof.json')
    tools = {}
    (out / 'tools').mkdir()
    for tool in (ROOT / 'tools/audit').glob('tmnt_native_storage_native*'):
        if tool.is_file(): shutil.copyfile(tool, out / 'tools' / tool.name);tools[tool.name] = sha(tool)
    artifacts = {str(path): sha(path) for label in labels for path in (pilots / label).iterdir() if path.is_file()}
    for label in ['baseline-hard', 'candidate-hard']:
        assert not (pilots / label / 'native-result.json').exists()
    report = f'''TMNT native audio current50b5/a983: EASY PERFORMANCE GATE FAILED
2026-10-25. No adoption; one sequential native grant RELEASED.

Accepted parent {CURRENT}
Candidate a9838664f94d29d87fbf4742e31d4e20d8b3a96862beabd11224afa4742d9003
Raw original pair and diagnostic replays: {pilots}
Frozen negative diagnosis: {out}

BOUND AND RESULT
Actual cold menu selected numericEasy0; both readbacks0. Same historical five
phases of120 updates (idle/walk/twoGoombas/primary/triplesecondary). Parent
authorized BEFORE-phase identical health128/equipment2/ammo99 setup; every
state write is logged and forbidden during the observed phase. No natural
acquisition claim, resource-result/RNG/audio-owner/sample/cadence injection.
Actual1-1 native floor/cache and both actorY184/feet208 guards pass.

Both complete600-update pilots PASS physical source/hardware/mixed4015/DMC,
NMI/IRQ/fiveSMC/stack/bank/CHR and immediate-complete OAM checks. Baseline572
versus candidate564 complete256-byte DMA transfers, all exact and inside
vblank/disabled rendering. Candidate54 actual active-DMC frames/540 correct
held-DAC44 frames. Actual rate15/non-loop/noIRQ/address/full129-byte sample
checked. Candidate602 source calls/2125 ordered original APUs pass. Diagnostic
replay additionally matches every188-byte source RAM/ZP state, with only
proven original-ROM-word pointer-high translation, against original executable.
No broad arbitrary RAM mask. Both diagnostic replays byte-match their original
gameplay, per-frame performance and routine-span CSVs exactly.

STRICT NEGATIVE
Idle/walk/enemies each0 added skipped draws. Primary adds2 (0→2), secondary
adds6 (28→34), eight total. Primary longest no-draw stall0→1; secondary stays1.
All196 absolute completed-update prefix deficits and145 phase-prefix deficits
remain in easy-strict-proof.json. All non-input game fields match; input-only
differences at532 and560 retained. Equal total929 frames does not override
lost draws. Hard was prepared but NOT run. Pause/events/reset/preemption and
full-song/roster native expansion were stopped after this failure.

FIRST CAUSAL DEADLINE
Same update406: baseline draw starts actual PPU735 scan162/dot317; candidate
starts735 scan191/dot325,3299 CPUcycles later. Baseline finishes update406 at
735 scan218/dot295; candidate finishes736 scan11/dot113, across an actual NMI.
Following update407 takes existing no-draw catch-up path. Preceding AudioUpdate
on735 costs baseline3014cycles versus candidate6283 (6163 excluding120 IRQ).
Candidate disjoint CPU: original-driver remainder3232 + writers561 + native
adapter165 + expanded wrapper151 + remaining outer/SFX/mixer2054 =6163.
Parent ExpandedAudioUpdate1063 + remaining outer1951 =3014. Thus this is an
observed music/SFX deadline burst, not a nearest-timestamp guess or sum of
nested durations. Exact component clocks/begin/end times in diagnosis.json.

Candidate AudioUpdate ends3267 CPUcycles later; the additional32 cycles
between audio return and draw admission remain a measured foreground residual
(consistent with DMC read halts), not a claimed complete DMA-stall attribution.
178 observed candidate direct DMC STA instructions all take4cycles/zeroextra;
subsequent DMA read halts must not be mislabeled STA execution time. Actual
source/hardware requests and pointer-state streams are retained.

TOTAL COST DISTRIBUTIONS
diagnosis.json contains per-phase mean/nearest-rankP95/max totalAudioUpdate
(including IRQ AND excluding IRQ), actual foregroundGameLoop excluding both
NMI/IRQ, and disjoint per-component distributions. Phase tags are actual entry
tags: final secondary119 spans plus startup1; no invented120th measurement.
Parent AudioUpdate means idle2932.93/walk3165.78/enemies3083.07/primary3268.80/
secondary3363.00. Candidate means2934.78/3053.05/3033.10/3241.25/3363.90.
Despite similar/lower means, candidate phaseP95 increases walk4509→5183,
enemies4065→4492, primary4536→5204, secondary4455→5054. Overall CPUpeak
parent5440→candidate7368 (7488 inclusiveIRQ). No native no-added-lag pass.

RETAINED HARNESS FAILURES AND LIMITS
Diagnostic preparationv1 incorrectly requested debug seg metadata on real
fixed-address Init/Play equates; no native ran. Diagnostic candidatev2 then
mistook private::Off/Owner labels for callable writers and failed an artificial
return decode. Failed scripts/logs remain. v3 profiles genuine public entries;
no game binary, gold/assertion or original stress workload changed. Baseline
diagnosticv2 remains its exact source/script hash and is not relabeledv3.

SOURCE-ONLY NEXT LEAD
Largest actual burst is authentic driver remainder, not only wrapper saves:
first-miss nativecore3793 CPUcycles includes561writers; peak source/writer
budgets and original channel-parser loops warrant a bounded instruction-level
profile. Owner-admission duplicate preservation is a smaller concrete adapter
lead (two status calls cost150/160 here), but cannot alone claim recovery of
the observed3269-cycle AudioUpdate burst. Preserve original rates/channels/
stores/data and re-prove all original16-song paths before any optimization.
All650 production inputs remain exact; no source/Git/Downloads installation.
'''
    (out / 'report.txt').write_text(report, encoding='utf-8')
    receipt = dict(frozen=True, accepted=False, performance_gate_passed=False, native_gate_failed=True,
                   baseline_ROM_sha256=CURRENT, candidate_ROM_sha256=results['candidate-easy']['ROM_sha256'],
                   actual_numeric_mode=0, Hard_prepared_not_run=True, native_worker_released=True,
                   initial_native_pair_guard_passed=True, added_draw_losses=8, primary_added=2, secondary_added=6,
                   diagnosis_sha256=sha(out / 'diagnosis.json'), strict_proof_sha256=sha(out / 'easy-strict-proof.json'),
                   report_sha256=sha(out / 'report.txt'), native_artifact_bindings=artifacts, tools=tools,
                   production_650_inputs_unchanged=True, no_audio_resource_owner_sample_cadence_outcome_injection=True)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(frozen=True, performance_gate_passed=False, receipt_sha256=sha(out / 'receipt.json'), source_tick=source_tick)))


if __name__ == '__main__':
    main()
