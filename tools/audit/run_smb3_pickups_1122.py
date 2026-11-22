"""Validate a6 SMB3 pickup scripts, or explicitly run them in Root's slot."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import build_storage_guard_v1 as Storage
from capture_budget import preflight
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import replay_smb3_pickups_1122 as Replay
from run_stdout_mesen_1110 import run

Current = Replay.Current
R, ROM, H = Replay.R, Replay.ROM, Replay.H
OUT = R / 'build/smb2-flag-native-1113'


def validate(raw):
    """Compile all four configurations without files, gameplay or processes."""
    def deny(*args, **kwargs):
        raise AssertionError('Source-only validation attempted files, process launch or gameplay')
    cases = []
    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), \
         patch('subprocess.Popen', deny), patch.object(Current.Frames, 'frame', deny), \
         patch.object(Current.N, 'invoke', deny):
        for form in Current.FORMS:
            for item in Current.ITEMS:
                script = Replay.controller(raw, form, item)
                q = Current.bindings(raw, form, item)
                assert q['character'] == 17 and q['slot'] == 16
                assert q['variant'] == Current.FORMS[form][0] and q['smc_return_pc'] == 0x016e
                cases.append(dict(form=form, item=item, controller_SHA256=H(script.encode()),
                                  hook_count=len(q['hooks']), ram_fields=len(q['ram'])))
        rejected = 0
        for dirty in (raw[:-1], raw[:100] + bytes((raw[100] ^ 1,)) + raw[101:]):
            try:
                Current.bindings(dirty)
            except AssertionError:
                rejected += 1
            else:
                raise AssertionError('Dirty or truncated ROM accepted')
    return dict(passed=True, ROM_SHA256=H(raw), cases=cases, dirty_rejections=rejected,
                files=0, emulator=False, actual_pickup_routes_verified=False)


def native(raw, forms, items, mode):
    """Root invokes this only after the shared queue is free."""
    before = check(ROM)
    assert before['ROM_sha256'] == Current.PIN == H(raw) and not before['matching_patch_files']
    rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert {p.name for p in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert rom.read_bytes() == raw, 'Use the existing exact installed candidate slot'
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    previous = script.read_bytes()
    failed = False
    try:
        for form in forms:
            for item in items:
                script.write_bytes(Replay.controller(raw, form, item, mode=mode).encode())
                result = run(script, ROM, OUT / 'capture', Current.PIN, 180)
                assert result['outputs_written'] == 0 and not result['images']
                receipt = result['receipt']
                summary = {key: receipt.get(key) for key in (
                    'passed', 'reason', 'form', 'route', 'difficulty', 'physical_frames',
                    'input_polls', 'updates', 'movement_updates', 'items', 'head', 'phase',
                    'counts', 'pending_returns', 'sound_writes', 'terminal', 'tail',
                )}
                summary.update(receipt_SHA256=result['receipt_SHA256'],
                               script_SHA256=result['script_SHA256'])
                print('SMB3 STOCK ' + json.dumps(summary, separators=(',', ':')), flush=True)
                assert ROM.read_bytes() == raw and check(ROM) == before
                if not result['passed']:
                    failed = True
                    return True  # Retain the first negative; no automatic route retry.
    finally:
        script.write_bytes(previous)
        assert rom.read_bytes() == raw and ROM.read_bytes() == raw and check(ROM) == before
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--validate', action='store_true', help='Default: in-memory source checks only')
    action.add_argument('--run', action='store_true', help='Root-only explicit shared-queue native run')
    parser.add_argument('--form', choices=(*Current.FORMS, 'both'), default='both')
    parser.add_argument('--item', choices=(*Current.ITEMS, 'both'), default='both')
    parser.add_argument('--mode', choices=('easy', 'hard'), default='easy')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    if not args.run:
        print('SMB3 SOURCE ' + json.dumps(validate(raw), separators=(',', ':')), flush=True)
        assert ROM.read_bytes() == raw
        return 0
    forms = tuple(Current.FORMS) if args.form == 'both' else (args.form,)
    items = tuple(Current.ITEMS) if args.item == 'both' else (args.item,)
    return int(native(raw, forms, items, args.mode))


if __name__ == '__main__':
    raise SystemExit(main())
