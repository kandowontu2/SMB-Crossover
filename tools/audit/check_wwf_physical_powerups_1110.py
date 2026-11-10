"""Serial actual-Mesen WWF pickup runs, with zero generated capture files."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import stage_wwf_powerups_1110 as Stage
from run_stdout_mesen_1110 import run

SCRIPT = Stage.R/'tools/playthroughs/wwf_earned_powerup_stdout_1110.lua'
SCRIPT_PIN = 'c98caae3c61adea500b15403d2eb6642ba29d758ece5f9f3492722d114817c79'
CANDIDATE = Stage.R/'build/wwf-powerups-native-1110/candidate.nes'


def compact(q):
    p = q['receipt']
    return dict(passed=q['passed'], role=p['role'], name=p['class_name'],
        ROM_SHA256=q['ROM_SHA256'], receipt_SHA256=q['receipt_SHA256'],
        script_SHA256=q['script_SHA256'], seconds=q['seconds'],
        frames=p['physical_frames'], Main=p['completed_Main'],
        collected=p.get('collected'), terminal=p['terminal'], ticks=p['powerup_ticks'],
        body_checks=p['hardware_checks'], recovery_checks=p['recovery_hardware_checks'],
        zero_completion_frames=p['zero_completion_frames'], output_files=q['outputs_written'],
        native_Mesen=True, other_processes_untouched=q['other_processes_untouched'],
        failure=None if q['passed'] else p)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--roles', type=int, nargs='+', choices=range(6), default=list(range(6)))
    args = ap.parse_args()
    assert len(set(args.roles)) == len(args.roles)
    assert CANDIDATE.read_bytes() == Stage.reconstruct()[0]
    assert sha256(SCRIPT.read_bytes()).hexdigest() == SCRIPT_PIN
    rows = []
    for role in args.roles:
        q = run(SCRIPT, CANDIDATE, args.output.resolve()/str(role), Stage.PIN, 150, role)
        row = compact(q)
        print(json.dumps(dict(event='WWF_actual_native', **row), sort_keys=True), flush=True)
        assert q['passed'] and q['receipt']['powerup_ticks'] == 60
        assert q['receipt']['terminal']['lives'] == 2
        assert q['receipt']['terminal']['x'] >= q['receipt']['collected']['x']+16
        assert q['receipt']['hardware_checks'] and q['receipt']['recovery_hardware_checks']
        rows.append(row)
    print(json.dumps(dict(passed=True, ROM_SHA256=Stage.PIN, actual_Mesen=True,
        roles=args.roles, rows=rows, output_files=0, shared_queue_serial=True), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
