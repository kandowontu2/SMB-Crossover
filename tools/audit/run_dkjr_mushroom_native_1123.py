"""Verify the proposed DK Jr. Mushroom lift in an isolated Mesen launch."""

import argparse
import json

import compose_dkjr_mushroom_scrooge_1123 as Initial
import compose_dkjr_mushroom_slot_order_1123 as Fixed
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_mario_luigi_stock_native_1122 import OUT as SHARED, R, ROM
from run_stdout_mesen_1110 import run


OUT = R / 'build' / 'dkjr-mushroom-native-1123'
FULL_RECEIPT = 'fe1de52fb1b4d6a1f0632734421801fd77c84a04df8b3f74ba21a2ed1f048d06'
FULL_CONTROLLER = '07c051dfc544c1b82004672d22d935a6c1f1b0d0c1d64b3e0428fdf7781d30a0'
PRIVATE_CHECKS = {
    'mushroom': 'be3ce07537c38cb5be9364f317776eb092835cafecf3bbbd9cbc04f96ce7c046',
    'cadence': '15fbf574b02410e689dd6a22f5360ae393856f2000c5a354f4a72f133f8833d8',
}


def controller(fix, raw, image, route):
    if route == 'full':
        source = fix.full_controller(image)
        if fix is Fixed:
            # Extend the existing ordinary back-facing jump to the next
            # riser where a standing forward jump catches the corner.
            old = 'if finalRiser>=4 and finalRiser<=6 then'
            assert source.count(old) == 1
            source = source.replace(old, 'if finalRiser>=3 and finalRiser<=6 then', 1)
            Fixed.Check.LuaRuntime().compile(source)
        return source.encode()
    if route == 'cadence':
        from install_dkjr_head_bridge_1123 import prepare

        reference = Initial.Scrooge.inverse(raw)
        _, programs = prepare(reference)
        program = programs['DONKEY KONG JR']
        digest = fix.H(reference).encode()
        assert program.count(digest) == 1
        return program.replace(digest, fix.CANDIDATE.encode(), 1)
    return fix.controller(image, route=route == 'approach').encode()


def test_native(fix, image, program, installed=False):
    OUT.mkdir()
    rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    path = ROM if installed else rom
    try:
        if not installed:
            rom.write_bytes(image)
        script.write_bytes(program)
        assert not check(path)['matching_patch_files']
        result = run(script, path, OUT / 'capture', fix.CANDIDATE, 320, long_no_capture=True)
        assert result['script_SHA256'] == fix.H(program)
        assert result['outputs_written'] == 0 and not result['images']
        assert path.read_bytes() == image and script.read_bytes() == program
        return result
    finally:
        script.unlink(missing_ok=True)
        rom.unlink(missing_ok=True)
        OUT.rmdir()


def deliver(raw, image, guard):
    assert Fixed.H(controller(Fixed, raw, image, 'full')) == FULL_CONTROLLER
    programs = {route: controller(Fixed, raw, image, route) for route in PRIVATE_CHECKS}
    require_free_workspace(R, ROM, allow_interactive=True)
    shared = SHARED / 'candidate.nes'
    assert not OUT.exists() and shared.read_bytes() == raw and check(ROM) == guard
    try:
        ROM.write_bytes(image)
        updated = check(ROM)
        assert updated['ROM_sha256'] == Fixed.CANDIDATE and not updated['matching_patch_files']
        for route, program in programs.items():
            result = test_native(Fixed, image, program, installed=True)
            print('DK JR DOWNLOADS ' + json.dumps(result, separators=(',', ':')), flush=True)
            assert result['passed'] and result['receipt_SHA256'] == PRIVATE_CHECKS[route], route
        shared.write_bytes(image)
        assert shared.read_bytes() == ROM.read_bytes() == image and check(ROM) == updated
    except BaseException:
        ROM.write_bytes(raw)
        if shared.read_bytes() != raw:
            shared.write_bytes(raw)
        assert shared.read_bytes() == ROM.read_bytes() == raw and check(ROM) == guard
        raise
    print('DK JR NIGHTLY INSTALLED ' + json.dumps(dict(guard=updated, full_1_1_receipt=FULL_RECEIPT),
                                                 separators=(',', ':')), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--route', choices=('mushroom', 'approach', 'full', 'cadence'))
    mode.add_argument('--deliver', action='store_true')
    parser.add_argument('--original-slot-order', action='store_true')
    args = parser.parse_args()
    fix = Initial if args.original_slot_order else Fixed
    guard = check(ROM)
    raw = ROM.read_bytes()
    assert guard['ROM_sha256'] == fix.H(raw) == fix.PIN and not guard['matching_patch_files']
    image, layout = fix.proposal(raw)
    assert layout['candidate_SHA256'] == fix.H(image) == fix.CANDIDATE
    if args.deliver:
        assert fix is Fixed
        return deliver(raw, image, guard)
    program = controller(fix, raw, image, args.route)
    try:
        result = test_native(fix, image, program)
    finally:
        assert ROM.read_bytes() == raw and check(ROM) == guard
    print('DK JR LIFT ' + json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
