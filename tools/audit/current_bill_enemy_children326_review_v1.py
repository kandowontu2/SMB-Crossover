"""Bounded read-only accounting of ROOT's current326 Bill timing replay.

Writes one small arithmetic receipt. Never launches native, decodes captures,
changes bound inputs, or converts replay exhaustion into a route pass.
"""
from pathlib import Path
import csv
import hashlib
import json
import statistics

R = Path(__file__).resolve().parents[2]
P = R / 'build/verification/bill-enemy-children326-ready-v2'
OLD = R / 'build/verification/bill-enemy-timing9ea-ready-v1'
OUT = R / 'build/bill_enemy_children326_review_v1.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    ready = json.loads((P / 'ready.json').read_text())
    assert sha(P / 'ready.json') == '17e998be6ddd22add32856ac3c96dbec57e78aa8a80be4fe30a2f81109c8e0e1'
    assert len(ready['bindings']) == 44
    for path, expected in ready['bindings'].items():
        assert sha(Path(path)) == expected, path
    launch = json.loads((P / 'launch.json').read_text())
    assert launch['exit_code'] == 1 and launch['changed_inputs'] == []
    assert launch['settings_before'] == launch['settings_after']
    log = (P / 'zelda2_easy_glove-run.log').read_text()
    assert 'FAIL Fixed replay stream exhausted' in log
    assert not (P / 'result.json').exists()
    assert (P / 'inputs.csv').read_bytes() == (OLD / 'inputs.csv').read_bytes()
    assert len(rows(P / 'inputs.csv')) == 6090

    summary = json.loads((P / 'bill-timing-summary.json').read_text())
    assert summary['timing_observation_complete'] and summary['open_interrupts'] == 0
    assert summary['ROM_sha256'] == '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
    raw_rows = rows(P / 'bill-timing.csv')
    data = [{k: int(v) for k, v in z.items()} for z in raw_rows]
    assert len(data) == 61 and [z['endframe_count'] for z in data] == list(range(3500, 3561))
    assert all(z['ppu_frame'] == z['endframe_count'] and z['ppu_line'] == 240 and z['ppu_dot'] == 0 for z in data)
    clocks = [z['cpu_cycle'] for z in data]
    intervals = [b - a for a, b in zip(clocks, clocks[1:])]
    assert set(intervals) == {29780, 29781}
    raw_csv = (P / 'bill-timing.csv').read_bytes()
    assert summary['csv_rows'] == 62 and len(raw_csv) - summary['csv_bytes'] == 62
    assert raw_csv.count(b'\r\n') == 62

    totals = {}
    for name, aggregate in summary['aggregate'].items():
        total = {k: sum(z[name + '_' + k] for z in data)
                 for k in ('calls', 'inclusive', 'exclusive', 'prewindow')}
        total['max'] = max(z[name + '_max'] for z in data)
        total['warmup_calls'] = aggregate['calls'] - total['calls']
        total['warmup_inclusive'] = aggregate['inclusive'] - total['inclusive']
        assert total['warmup_calls'] >= 0 and total['warmup_inclusive'] >= 0
        totals[name] = total
    ranked = sorted((dict(name=n, **z) for n, z in totals.items() if n != 'AudioUpdate'),
                    key=lambda z: -z['exclusive'])
    # Completed descendants of an open parent remain real measurements.
    children = ['EnemyGraphicsEngine', 'EnemyMovementSubs', 'ProcLoopCommand',
                'Mmc5GroundGoombaTerrain', 'PlayerEnemyCollision']
    overhang = totals['EnemiesAndLoopsCore']['exclusive'] + sum(totals[n]['inclusive'] for n in children) - totals['EnemiesAndLoopsCore']['inclusive']
    assert overhang == data[-1]['EnemyGraphicsEngine_inclusive'] == 134
    assert data[-1]['EnemyGraphicsEngine_calls'] == 1 and data[-1]['EnemiesAndLoopsCore_calls'] == 0
    assert [(z['name'], z['frame']) for z in summary['open_spans_censored']] == [('GameLoop', 3560), ('EnemiesAndLoopsCore', 3560)]
    recovered = sum(totals[n]['inclusive'] for n in children[:3]) - overhang
    assert recovered == 59490 and totals['EnemiesAndLoopsCore']['exclusive'] + recovered == 143207
    foreground_exclusive = sum(z['exclusive'] for n, z in totals.items() if n != 'AudioUpdate')
    assert foreground_exclusive == 1137601
    boundary_residual = foreground_exclusive - totals['GameLoop']['inclusive']
    assert boundary_residual == -4046 and totals['GameLoop']['prewindow'] == 1
    aggregate_foreground = sum(z['exclusive'] for n, z in summary['aggregate'].items() if n != 'AudioUpdate')
    assert aggregate_foreground - foreground_exclusive == 15484

    main_costs = []
    for z in data:
        n = z['GameLoop_calls']
        assert n in (0, 1, 2)
        if n:
            main_costs.append(z['GameLoop_max'])
            if n == 2:
                main_costs.append(z['GameLoop_inclusive'] - z['GameLoop_max'])
    assert len(main_costs) == 40 and sum(main_costs) == totals['GameLoop']['inclusive']
    states = {k: dict(sorted(__import__('collections').Counter(z[k] for z in data).items()))
              for k in ('state', 'weapon', 'ordinary_shots', 'advanced_shots', 'other_shots',
                        'enemy_slots', 'timer', 'powerup', 'refill')}
    assert all(z['weapon'] == z['advanced_shots'] == z['other_shots'] == z['timer'] == z['powerup'] == z['refill'] == 0 for z in data)

    old_data = rows(OLD / 'bill-timing.csv')
    workload_keys = ('x', 'y', 'state', 'buttons', 'weapon', 'ordinary_shots', 'advanced_shots',
                     'other_shots', 'enemy_slots', 'timer', 'powerup', 'refill', 'dmas', 'loops_closed')
    old_diff = {k: sum(a[k] != b[k] for a, b in zip(old_data, raw_rows)) for k in workload_keys}
    route = rows(P / 'trace.csv')
    old_route = rows(OLD / 'trace.csv')
    assert len(route) == 6091 and int(route[-1]['poll']) == 6090
    terminal = {}
    for name, stream in [('current326', route), ('old9ea', old_route)]:
        active12 = [z for z in stream if z['world'] == '0' and z['level'] == '1' and z['engine'] == '8' and z['task'] == '3']
        terminal[name] = dict(first_active12_sample=active12[0], last_sample=stream[-1],
                              completed_Main_ID_interval=[int(active12[0]['loops']), int(active12[-1]['loops'])])
    assert terminal['current326']['completed_Main_ID_interval'] == [5118, 5139]
    assert terminal['old9ea']['completed_Main_ID_interval'] == [5118, 5142]
    source_files = ['src/game.s', 'src/object.s', 'src/sprite_render.s', 'src/level_tiles.s',
                    'src/collision.s', 'src/metasprite_engine.s', 'src/remaining_weapons.s',
                    'tools/audit/current_roster_compact_11_v1.lua', 'build/bill_early_cache_timing_full.lua']
    artifacts = ['bill-timing-summary.json', 'bill-timing.csv', 'inputs.csv', 'trace.csv',
                 'launch.json', 'zelda2_easy_glove-run.log', 'profile-config.json', 'prepare-controls.json']
    receipt = dict(
        passed_read_only_arithmetic=True, route_pass=False, native_exit_code=1,
        native_reason='Fixed replay stream exhausted; no result.json or controlled endpoint PASS',
        ROM_sha256=summary['ROM_sha256'], unchanged_strict_bindings=44,
        timing_rows=61, physical_frames=[3500, 3560], first_last_clock=[clocks[0], clocks[-1]],
        PPU_intervals=sorted(set(intervals)), totals=totals, foreground_exclusive_rank=ranked,
        completed_foreground_exclusives=foreground_exclusive, closed_Main_inclusive=totals['GameLoop']['inclusive'],
        boundary_residual=boundary_residual, aggregate_foreground_exclusive=aggregate_foreground,
        warmup_foreground_exclusives=15484, censored=summary['open_spans_censored'],
        censored_EnemyCore_graphics_descendant=134, new_children_in_completed_EnemyCore=59490,
        measured_Main=dict(calls=40, mean=statistics.mean(main_costs), median=statistics.median(main_costs),
                           maximum=max(main_costs), above_29781=sum(x > 29781 for x in main_costs)),
        interrupt_and_dma_totals={k: sum(z[k] for z in data) for k in
                                 ('nmi_closed', 'nmi_elapsed', 'irq_closed', 'irq_elapsed', 'dmas', 'lag_counter_delta')},
        state_samples=states, old9ea_workload_different_rows=old_diff, route_terminal=terminal,
        artifacts={str((P / n).relative_to(R)): sha(P / n) for n in artifacts},
        source_bindings={n: sha(R / n) for n in source_files}, tool_sha256=sha(Path(__file__)),
        limits='Completion buckets, not per-frame integrals or the same closed-Main cohort. No per-call EnemyID/pose/cache flags or exact closed-span serial IDs. EndFrame state is a sample; cold/paused/refill exclusions are observed only there. NMI elapsed includes nested IRQ, so do not add ISR totals. Audio excludes interrupt time. First Main began3499; final Main/EnemyCore remain censored. No capture decode/new images, source edits, native launch, route pass, matched FPS or optimization claim.')
    OUT.write_text(json.dumps(receipt, indent=2) + '\n', newline='\n')
    print(json.dumps(dict(passed_read_only_arithmetic=True, route_pass=False,
                         output=str(OUT), sha256=sha(OUT), measured_Main=receipt['measured_Main'])))


if __name__ == '__main__':
    main()
