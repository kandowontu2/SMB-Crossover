"""Strict same-work native TMNT pilot comparison, retaining every deficit."""
from pathlib import Path
import argparse
import csv
import json
import statistics
from tmnt_native_storage_driver import ROOT, sha


def read(path):
    with path.open() as stream: return list(csv.DictReader(stream))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT) and not a.output.exists()
    reports = [json.loads((folder / 'native-result.json').read_text()) for folder in [a.baseline, a.candidate]]
    assert all(row['passed'] for row in reports)
    assert reports[0]['behavior'] == reports[1]['behavior']
    assert reports[0]['dependencies'] == reports[1]['dependencies']
    games = [read(folder / 'gameplay.csv') for folder in [a.baseline, a.candidate]]
    assert len(games[0]) == len(games[1]) == 600
    differences = []
    for index, (x, y) in enumerate(zip(*games)):
        diff = {name: [x[name], y[name]] for name in x if x[name] != y[name]}
        if diff: differences.append(dict(update=index, fields=diff))
    same_work = not any(name != 'input' for row in differences for name in row['fields'])
    ledgers = [[json.loads(line) for line in (folder / 'native-bus.jsonl').read_text().splitlines()]
               for folder in [a.baseline, a.candidate]]
    completed = [[row for row in ledger if row['kind'] == 'completed-game-update'] for ledger in ledgers]
    assert len(completed[0]) == len(completed[1]) == 600
    assert all(row['index'] == i + 1 for rows in completed for i, row in enumerate(rows))
    absolute_prefix_deficits, phase_prefix_deficits = [], []
    start_frames = [rows[0]['stamp']['frame'] for rows in completed]
    start_draws = [rows[0]['draws'] for rows in completed]
    phase_start = {}
    for index, (x, y) in enumerate(zip(*completed)):
        assert x['phase'] == y['phase']
        phase = x['phase']
        phase_start.setdefault(phase, index)
        added_frames = (y['stamp']['frame'] - start_frames[1]) - (x['stamp']['frame'] - start_frames[0])
        lost_draws = (x['draws'] - start_draws[0]) - (y['draws'] - start_draws[1])
        if added_frames > 0 or lost_draws > 0:
            absolute_prefix_deficits.append(dict(update=index + 1, phase=phase, added_physical_frames=added_frames, fewer_draw_constructions=lost_draws))
        at = phase_start[phase]
        px, py = completed[0][at], completed[1][at]
        phase_frames = (y['stamp']['frame'] - py['stamp']['frame']) - (x['stamp']['frame'] - px['stamp']['frame'])
        phase_draws = (x['draws'] - px['draws']) - (y['draws'] - py['draws'])
        if phase_frames > 0 or phase_draws > 0:
            phase_prefix_deficits.append(dict(update=index + 1, phase=phase, added_physical_frames=phase_frames, fewer_draw_constructions=phase_draws))
    phases = {}
    no_added = True
    for phase in ['idle', 'walk', 'enemies', 'primary', 'secondary']:
        stats = {}
        for label, folder, states in zip(['baseline', 'candidate'], [a.baseline, a.candidate], games):
            assert sum(row['phase'] == phase for row in states) == 120
            if phase == 'enemies':
                assert sum(row['phase'] == phase and (int(row['enemy0']) or int(row['enemy1'])) for row in states) >= 120
            frames = [row for row in read(folder / 'tmnt-performance-frames.csv') if row['phase'] == phase]
            spans = [row for row in read(folder / 'tmnt-performance-calls.csv') if row['phase'] == phase]
            run = longest = 0
            for row in frames:
                run = run + 1 if int(row['draws']) == 0 else 0
                longest = max(longest, run)
            q = dict(physical_frames=len(frames), lag_NMIs=sum(int(row['lagNmis']) for row in frames),
                     completed_frame_draw_constructions=sum(int(row['draws']) for row in frames),
                     longest_consecutive_physical_frames_without_draw=longest,
                     movement_updates=sum(int(row['updates']) for row in frames))
            for name in ['GameLoop', 'DrawAllMetasprites', 'TnDrawEquipment']:
                cycles = [int(row['cpuCycles']) for row in spans if row['name'] == name]
                assert cycles, (phase, label, name)
                q[name] = dict(calls=len(cycles), mean_foreground_cycles=statistics.mean(cycles), peak_foreground_cycles=max(cycles))
            stats[label] = q
        stats['added_lag_NMIs'] = stats['candidate']['lag_NMIs'] - stats['baseline']['lag_NMIs']
        stats['longest_stall_change'] = stats['candidate']['longest_consecutive_physical_frames_without_draw'] - stats['baseline']['longest_consecutive_physical_frames_without_draw']
        no_added &= stats['added_lag_NMIs'] <= 0 and stats['longest_stall_change'] <= 0
        phases[phase] = stats
    result = dict(passed=same_work and no_added and not absolute_prefix_deficits and not phase_prefix_deficits,
                  measurement_valid=same_work, both_native_guard_suites_passed=True,
                  performance_gate_passed=same_work and no_added and not absolute_prefix_deficits and not phase_prefix_deficits,
                  behavior=reports[0]['behavior'], baseline_ROM_sha256=reports[0]['ROM_sha256'], candidate_ROM_sha256=reports[1]['ROM_sha256'],
                  gameplay_differences=differences, phases=phases,
                  all_completed_update_prefix_deficits=absolute_prefix_deficits,
                  all_phase_prefix_deficits=phase_prefix_deficits,
                  native_result_sha256=[sha(folder / 'native-result.json') for folder in [a.baseline, a.candidate]],
                  checker_sha256=sha(Path(__file__)), accepted=False,
                  limits='One explicitly staged same-work600-update arena per actual cold numeric mode; foreground spans exclude ISR bodies and include real DMA stalls. All deficits retained, no universal cadence or natural gear acquisition claim.')
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], measurement_valid=same_work, behavior=result['behavior'],
                          phases={name: dict(added_lag=q['added_lag_NMIs'], added_longest_stall=q['longest_stall_change']) for name, q in phases.items()},
                          absolute_prefix_deficits=len(absolute_prefix_deficits), phase_prefix_deficits=len(phase_prefix_deficits), gameplay_differences=len(differences))))
    raise SystemExit(0 if result['passed'] else 2)


if __name__ == '__main__':
    main()
