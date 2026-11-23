"""Test Scrooge's hidden 1-UP pogo fix in Mesen before nightly delivery."""

import argparse
import json

import compose_scrooge_prepare_stack_1123 as Fix
from mesen_session_guard_v1 import require_free_workspace
from run_mario_luigi_stock_native_1122 import OUT as SHARED, R, ROM
from run_stdout_mesen_1110 import run
from nightly_patch_guard_v1 import check


OUT = R / 'build' / 'scrooge-pogo-prepare-native-1123'
EXPECTED = '82e8da0e293dee91da441347dfe4c675c88708c43b0b88d4fbd253312f00a131'
SCRIPTS = {
    'life': '06850f0ab745d52e342ffdd8edb993d1db77cd785fdbe23cd98d78749976102e',
    'star': '0e96882524267cc59fdec4d9ef0269f74cd2cb309331f6e2a55533fa32d2d721',
}
PRIVATE_RECEIPTS = {
    'life': 'cb19b664f8ee78f38993aece44cf18937d4d20e7fd2fcd51dea56b1d0b2b87a5',
    'star': '9f115dd24e8dc32097c0fb86fce2d51299490f3c12ef6db791dce4955d7092b8',
}


def controller(candidate, route):
    if route == 'life':
        return Fix.controller(candidate).encode()
    parent = Fix.Bridge.inverse(Fix.inverse(candidate))
    stock = Fix.D.Stock
    source = stock.controller(parent, 'scrooge', 'star').decode()
    source = stock.once(source, stock.H(parent), EXPECTED)
    source = stock.once(source, 'if C.char==5 then\n   local food=followFirstFood(c)',
                        'if C.char==5 or C.char==12 then\n   local food=followFirstFood(c)')
    stock.LuaRuntime().compile(source)
    return source.encode()


def test_native(candidate, route, installed):
    program = controller(candidate, route)
    script_sha = SCRIPTS[route]
    assert Fix.H(program) == script_sha
    OUT.mkdir()
    rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    try:
        if not installed:
            rom.write_bytes(candidate)
        script.write_bytes(program)
        launch_path = ROM if installed else rom
        assert not check(launch_path)['matching_patch_files']
        result = run(script, launch_path, OUT / 'capture', EXPECTED, 190)
        assert result['script_SHA256'] == script_sha and result['outputs_written'] == 0 and not result['images']
        assert launch_path.read_bytes() == candidate and script.read_bytes() == program
    finally:
        script.unlink(missing_ok=True)
        rom.unlink(missing_ok=True)
        OUT.rmdir()
    return result


def deliver(raw, candidate, guard):
    require_free_workspace(R, ROM, allow_interactive=True)
    shared_rom = SHARED / 'candidate.nes'
    assert not OUT.exists() and shared_rom.read_bytes() == raw and check(ROM) == guard
    try:
        ROM.write_bytes(candidate)
        updated_guard = check(ROM)
        assert updated_guard['ROM_sha256'] == EXPECTED and not updated_guard['matching_patch_files']
        for route, expected in PRIVATE_RECEIPTS.items():
            result = test_native(candidate, route, installed=True)
            print('SCROOGE DOWNLOADS ' + json.dumps(result, separators=(',', ':')), flush=True)
            assert result['passed'] and result['receipt_SHA256'] == expected, route
        assert ROM.read_bytes() == candidate and check(ROM) == updated_guard
        shared_rom.write_bytes(candidate)
        assert shared_rom.read_bytes() == ROM.read_bytes() == candidate
    except BaseException:
        ROM.write_bytes(raw)
        if shared_rom.read_bytes() != raw:
            shared_rom.write_bytes(raw)
        assert ROM.read_bytes() == shared_rom.read_bytes() == raw and check(ROM) == guard
        raise
    print('SCROOGE NIGHTLY INSTALLED ' + json.dumps(updated_guard, separators=(',', ':')), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', choices=tuple(SCRIPTS), default='life')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--installed', action='store_true')
    mode.add_argument('--deliver', action='store_true')
    args = parser.parse_args()
    guard = check(ROM)
    raw = ROM.read_bytes()
    assert guard['ROM_sha256'] == Fix.H(raw) and not guard['matching_patch_files']
    if args.installed:
        assert Fix.H(raw) == EXPECTED
        candidate = raw
    else:
        assert Fix.H(raw) == Fix.PIN
        candidate, composition = Fix.proposal(raw)
        assert composition['candidate_SHA256'] == EXPECTED == Fix.H(candidate)
    if args.deliver:
        return deliver(raw, candidate, guard)
    try:
        result = test_native(candidate, args.route, args.installed)
    finally:
        assert ROM.read_bytes() == raw and check(ROM) == guard
    print('SCROOGE POGO NATIVE ' + json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
