"""Preserve the three-byte source optimization, native route, and remaining lag."""
from pathlib import Path
from collections import Counter
import csv
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save, sha

O = R/'build/rogue-current-menu-v8'


def main():
    bindings = {}
    for name in ['build-proof.json', 'controls.json', 'prune-controls.json']:
        path = O/name
        receipt = json.loads(path.read_text())
        bindings.update(receipt['source_bindings'])
        bindings[str(path)] = sha(path)
    controls = json.loads((O/'prune-controls.json').read_text())
    assert controls['passed'] and len(controls['UI_cases']) == 96
    assert len(controls['changed_ROM_offsets']) == 3
    assert all(not case['dead_farcall_operand_differences'] for case in controls['UI_cases'])
    route_path = O/'native/route/review.json'
    route = json.loads(route_path.read_text())
    assert route['passed'] and route['full_frame_comparison']['exact_pairs'] == 5796
    bindings.update(route['inputs'])
    bindings[str(route_path)] = sha(route_path)
    bill = O/'native/bill-candidate-v1'
    result = json.loads((bill/'result.json').read_text())
    assert result['passed'] and result['main_updates'] == 299 and result['timing']['lag_nmi'] == 26
    bind = json.loads((bill/'binding.json').read_text())
    assert bind['exit_code'] == 0
    bindings.update(bind['inputs'])
    budget = json.loads((bill/'capture-budget.json').read_text())
    assert budget['returncode'] == 0 and not budget['violations']
    cycles = list(csv.DictReader((bill/'main-cycles.csv').open()))
    mean = sum(int(row['foreground_cpu']) for row in cycles)/len(cycles)
    trace = list(csv.DictReader((bill/'trace.csv').open()))
    game = trace[-300:]
    preceding = trace[-301]
    histogram = Counter()
    for row in game:
        histogram[int(row['main_updates'])-int(preceding['main_updates'])] += 1
        preceding = row
    assert histogram == {0: 32, 1: 237, 2: 31}, histogram
    for path in bill.iterdir():
        if path.is_file():
            bindings[str(path)] = sha(path)
    negatives = [R/'build/rogue-current-menu-v7/capacity-negative.json',
                 R/'build/rogue-current-menu-v7/compile-log.json',
                 R/'build/rogue-current-menu-v7/driver-failed-build.py',
                 O/'negative-cost-prediction/reason.json',
                 O/'negative-cost-prediction/controls.json',
                 O/'negative-cost-prediction/menu-controls-adapter.py',
                 O/'controls-cost-prediction-draft.py']
    tools = ['prepare_rogue_foreign_prune_v1.py', 'rogue_foreign_prune_controls_v2.py',
             'rogue_foreign_prune_native_v1.py', 'rogue_foreign_prune_route_v1.py',
             'review_rogue_foreign_prune_route_v1.py']
    for path in negatives+[R/'tools/audit'/name for name in tools]+[Path(__file__).resolve()]:
        bindings[str(path)] = sha(path)
    for path, digest in bindings.items():
        assert sha(path) == digest, path
    save('rogue-foreign-ui-prune', dict(
        status='NATIVE_ROUTE_PARITY_PASS_FOREIGN_TIMING_IMPROVED_STILL_REGRESSES_PRIVATE_ONLY',
        ROM_sha256=controls['ROM_sha256'], changed_ROM_bytes=3,
        source_UI_cases=96, all_existing_symbol_addresses_exact=True,
        source_CPU_savings=dict(foreign_ordinary=114, foreign_Samus=122, own_Rogue=0),
        source_ABI='AXYP/SP, application/live stack, maps, all33SMCbytes and ordered nonmapper writes match.',
        native_route=dict(frames=6513, verified_lossless_frames=5801, exact_reference_pixels=5796,
                          changed_menu_frames=5, real_1_2_updates=25, zero_deaths=True, cheats_off=True),
        root_visual_review='Viewed the actual eight-frame contact sheet and separate castle walk: colored Rogue menu body, lives/body, overworld, power change, flagpole, castle and underground endpoint visible.',
        native_Bill=dict(frames=300, completed_Main=299, lag_NMIs=26,
                         completion_histogram=dict(histogram), mean_foreground_CPU=mean,
                         previous_Rogue_V6_lag_NMIs=33, installed_parent_lag_NMIs=4,
                         installed_parent_mean_CPU=21514.72575),
        retained_negatives=['Five-byte growth rejected by the genuine full A95 source capacity guard.',
                            'Initial exact ABI pass reached a numeric Samus cost-prediction error; 122CPU corrected in a separate verifier.'],
        limits=['The shared download remains unchanged; 26lagNMIs still exceed the installed baseline4.',
                'Mean CPU does not improve in this native mix: V6mean22678.84228 versus V8mean22690.71572.',
                'All5801 checksums and pixel comparisons do not imply exhaustive human inspection or source perfection.',
                'No all-upgrade/Hard/full-campaign/constant60Hz/physical-hardware admission.']), bindings)


if __name__ == '__main__':
    main()
