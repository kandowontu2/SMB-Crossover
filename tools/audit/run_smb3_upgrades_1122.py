"""Source-only validation by default; explicit Root native Mushroom/suit runs."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import build_storage_guard_v1 as Storage
from capture_budget import preflight
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import replay_smb3_upgrades_1122 as Replay
from run_stdout_mesen_1110 import run

Current = Replay.Current
R, ROM, H, PIN = Replay.R, Replay.ROM, Replay.H, Replay.PIN
OUT = R / 'build/smb2-flag-native-1113'


def validate(raw):
    def deny(*args, **kwargs):
        raise AssertionError('Source-only upgrades attempted files, process launch or gameplay')
    cases = []
    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), \
         patch('subprocess.Popen', deny), patch.object(Current.Frames, 'frame', deny), \
         patch.object(Current.N, 'invoke', deny):
        for form in Current.FORMS:
            for route in Current.ROUTES:
                text = Replay.controller(raw, form, route)
                q = Current.bindings(raw, form, route)
                assert q['sha'] == PIN and q['character'] == 17 and q['slot'] == 16
                cases.append(dict(form=form, route=route, controller_SHA256=H(text.encode()),
                                  hooks=len(q['hooks']), ram_fields=len(q['ram'])))
        rejected = 0
        for wrong in (raw[:-1], raw[:100] + bytes((raw[100] ^ 1,)) + raw[101:], Current.Stock.Beans.inverse(raw)):
            try:
                Current.bindings(wrong)
            except AssertionError:
                rejected += 1
            else:
                raise AssertionError('Wrong ROM accepted by strict32 upgrade adapter')
    return dict(passed=True, ROM_SHA256=PIN, cases=cases, strict_rejections=rejected,
                files=0, emulator=False, actual_natural_upgrades_verified=False)


def native(raw, forms, route, mode):
    before = check(ROM)
    assert H(raw) == PIN == before['ROM_sha256'] and not before['matching_patch_files']
    candidate, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert {p.name for p in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    assert candidate.read_bytes() == raw
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    previous = script.read_bytes()
    try:
        for form in forms:
            script.write_bytes(Replay.controller(raw, form, route, mode=mode).encode())
            result = run(script, ROM, OUT / 'capture', PIN, 180)
            assert not result['images'] and result['outputs_written'] == 0
            receipt = result['receipt']
            summary = {key: receipt.get(key) for key in (
                'passed', 'reason', 'form', 'route', 'difficulty', 'physical_frames',
                'updates', 'movement_updates', 'items', 'head', 'phase', 'counts',
                'pending_returns', 'terminal', 'tail', 'logical_item_policy',
            )}
            summary['completed_checkpoints'] = [key for key, q in receipt.get('items', {}).items() if q.get('after')]
            summary.update(receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'])
            print('SMB3 UPGRADES ' + json.dumps(summary, separators=(',', ':')), flush=True)
            assert ROM.read_bytes() == raw and check(ROM) == before
            if not result['passed']:
                return 1
    finally:
        script.write_bytes(previous)
        assert candidate.read_bytes() == raw and ROM.read_bytes() == raw and check(ROM) == before
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--validate', action='store_true')
    action.add_argument('--run', action='store_true', help='Root-only explicit shared Mesen queue')
    parser.add_argument('--form', choices=(*Current.FORMS, 'both'), default='both')
    parser.add_argument('--route', choices=Current.ROUTES, default='mushroom-suit')
    parser.add_argument('--mode', choices=('easy', 'hard'), default='easy')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    if not args.run:
        print('SMB3 UPGRADE SOURCE ' + json.dumps(validate(raw), separators=(',', ':')), flush=True)
        assert ROM.read_bytes() == raw
        return 0
    forms = tuple(Current.FORMS) if args.form == 'both' else (args.form,)
    return native(raw, forms, args.route, args.mode)


if __name__ == '__main__':
    raise SystemExit(main())
