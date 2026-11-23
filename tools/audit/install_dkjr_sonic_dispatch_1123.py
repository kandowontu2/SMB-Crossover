"""Install the native-tested dispatcher and check the actual Downloads launch."""

import argparse
import json

from check_ff_stdout_controller_source_1110 import LuaRuntime
import compose_dkjr_sonic_dispatch_1123 as Combined
import compose_sonic_current_auth_epoch_1122 as Sonic
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import repair_rogue_side_pipe_1123 as Pipe
import run_roster_empty_cadence_1122 as Roster
from run_stdout_mesen_1110 import run


PROOFS = {
    'DONKEY KONG JR': '0fcb4c740d491c870383e2088a0f44737e51ca4ab478f6ab0d3f6477cb0b0a04',
    'SONIC': '4d48ea7af82073761a2097ab95a63ef31a7eb7768619dd3201d70f1c780e0dba',
    'SUPER SONIC': 'b10d8dfbba98f6dbbdc8da889ccbb43650e0dd95789bde15964564f946b18333',
    'MINI MARIO': '0ea949314ac1f8c41671478b928ff2fe92bfd253f714ad1da5d4985d83cbc788',
}
PRIVATE_CADENCE = {
    'DONKEY KONG JR': 'f9fd3f2c8a605e35959bf8563534e16a9039ee9f9a606bdc2f68d6cfbf14b84c',
    'MINI MARIO': PROOFS['MINI MARIO'],
}


def prepare(installed):
    parent = Combined.inverse(installed) if Combined.H(installed) == Combined.CANDIDATE else installed
    candidate, _ = Combined.proposal(parent)
    assert Combined.inverse(candidate) == parent
    reference = Sonic.inverse(Pipe.restore_pipe_bytes(parent))
    rows = Roster.roster(reference)
    programs = {}
    for name in PROOFS:
        control = Roster.controller(reference, rows[name])
        assert control.count(Roster.Timing.PIN) == 1
        control = control.replace(Roster.Timing.PIN, Combined.CANDIDATE, 1)
        LuaRuntime().compile(control)
        programs[name] = control.encode()
    return candidate, programs


def guard(path, digest):
    result = check(path)
    assert result['passed'] and result['ROM_sha256'] == digest and not result['matching_patch_files']


def deliver(installed, candidate, programs):
    rom = Roster.Timing.ROM
    out = Roster.Timing.SHARED
    target, script = out/'candidate.nes', out/'controller.lua'
    assert set(out.iterdir()) == {target, script}
    assert rom.read_bytes() == target.read_bytes() == installed
    installed_sha = Combined.H(installed)
    guard(rom, installed_sha)
    guard(target, installed_sha)
    require_free_workspace(Roster.Timing.R, rom, allow_interactive=True)
    previous = script.read_bytes()
    verified = False
    try:
        if installed != candidate:
            rom.write_bytes(candidate)
            target.write_bytes(candidate)
        guard(rom, Combined.CANDIDATE)
        guard(target, Combined.CANDIDATE)
        for name, program in programs.items():
            script.write_bytes(program)
            result = run(script, rom, out/'capture', Combined.CANDIDATE, 90)
            receipt = result['receipt']
            assert result['passed'] and not result['images'] and result['outputs_written'] == 0
            assert result['script_SHA256'] == Combined.H(program) and receipt['character'] == name
            assert receipt['measured_Main'] == 64
            fields = ('character', 'measured_Main', 'inclusive_video_frames',
                      'no_controller_read_frames', 'native_lag_NMI')
            row = {key: receipt[key] for key in fields}
            row['receipt_SHA256'] = result['receipt_SHA256']
            if name in PRIVATE_CADENCE:
                row['private_receipt_match'] = result['receipt_SHA256'] == PRIVATE_CADENCE[name]
            print('COMBINED DOWNLOADS CADENCE '+json.dumps(row,separators=(',',':')), flush=True)
            if name == 'DONKEY KONG JR':
                assert receipt['inclusive_video_frames'] < 128, row
            if name == 'MINI MARIO':
                assert receipt['inclusive_video_frames'] == 64 and receipt['no_controller_read_frames'] == 0, row
                assert receipt['native_lag_NMI'] == 0, row
        assert rom.read_bytes() == target.read_bytes() == candidate
        guard(rom, Combined.CANDIDATE)
        guard(target, Combined.CANDIDATE)
        verified = True
    finally:
        script.write_bytes(previous)
        if not verified and installed != candidate:
            rom.write_bytes(installed)
            target.write_bytes(installed)
            guard(rom, installed_sha)
            guard(target, installed_sha)
        assert set(out.iterdir()) == {target, script}
        assert script.read_bytes() == previous
    print('COMBINED NIGHTLY DELIVERED '+json.dumps(dict(ROM_SHA256=Combined.CANDIDATE,
          private_receipts=PROOFS, Downloads_standing_and_walking=list(programs), backups=0)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installed = Roster.Timing.ROM.read_bytes()
    candidate, programs = prepare(installed)
    print('COMBINED NIGHTLY SOURCE '+json.dumps(dict(ROM_SHA256=Combined.H(candidate),
          scripts={name:Combined.H(program) for name,program in programs.items()})), flush=True)
    if args.install:
        deliver(installed, candidate, programs)


if __name__ == '__main__':
    main()
