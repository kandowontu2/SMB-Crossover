"""Measure the shared sprite scan change in the real MMC5 empty stage opening."""

import argparse
from hashlib import sha256
import json

import compose_sparse_sprite_scan_1123 as Sparse
import run_roster_empty_cadence_current_1123 as Current


Previous, Timing = Current.Previous, Current.Previous.Timing
TARGETS = ('BASS', 'DONKEY KONG', 'STEVE HERMANN', 'MINI MARIO')


def run(names, compose=Sparse.compose):
    downloads = Previous.check(Timing.ROM)
    parent = Timing.ROM.read_bytes()
    candidate = compose(parent)
    digest = sha256(candidate).hexdigest()
    reference = Current.reference(parent)
    roster = Previous.roster(parent)
    work = Timing.SHARED
    rom, controller = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, controller} and rom.read_bytes() == parent
    Previous.require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)
    old_controller = controller.read_bytes()
    try:
        rom.write_bytes(candidate)
        candidate_guard = Previous.check(rom)
        assert candidate_guard['ROM_sha256'] == digest
        for name in names:
            script = Current.controller(reference, roster[name])
            assert script.count(Timing.PIN) == 1
            controller.write_bytes(script.replace(Timing.PIN, digest, 1).encode())
            proof = Previous.run(controller, rom, work / 'capture', digest, 90)
            assert proof['outputs_written'] == 0 and not proof['images']
            data = proof['receipt']
            selected = ('passed', 'reason', 'character', 'phases', 'terminal',
                        'inclusive_video_frames', 'measured_Main', 'no_controller_read_frames',
                        'native_lag_NMI', 'inclusive_Main_costs', 'Main_return_histogram')
            report = {key: data[key] for key in selected if key in data}
            report.update(ROM=digest, receipt_SHA256=proof['receipt_SHA256'], script_SHA256=proof['script_SHA256'])
            print('SPARSE DRAW MESEN ' + json.dumps(report, separators=(',', ':')), flush=True)
            assert proof['passed'], (name, data['reason'])
            assert Previous.check(rom) == candidate_guard
    finally:
        rom.write_bytes(parent)
        controller.write_bytes(old_controller)
        assert set(work.iterdir()) == {rom, controller}
        assert rom.read_bytes() == Timing.ROM.read_bytes() == parent
        assert Previous.check(Timing.ROM) == downloads


if __name__ == '__main__':
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('characters', nargs='+', choices=TARGETS)
    run(args.parse_args().characters)
