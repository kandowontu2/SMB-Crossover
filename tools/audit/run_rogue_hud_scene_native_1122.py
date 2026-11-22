"""Verify Rogue Dawn's HUD across the area change and install the tested nightly."""

import argparse
import json

import capture_budget
from compose_rogue_hud_scene_dirty_cb95_1116 import CANDIDATE, H, PARENT, R, ROM, proposal
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from replay_rogue_hud_scene_dirty79fd_1116 import controller
from run_stdout_mesen_1110 import run


OUT = R / 'build/smb2-flag-native-1113'
CANDIDATE_ROM = OUT / 'candidate.nes'
SCRIPT = OUT / 'controller.lua'
HUD_ROW = [14, 1, 9, 1, 36, 22, 0, 0, 5, 36, 36]  # E191 M005
KINDS = ('hud', 'missile', 'full')


def assert_patch_free(rom, expected):
    status = check(rom)
    assert status['ROM_sha256'] == expected and not status['matching_patch_files'], status


def validate(rom, raw, kind):
    lua = controller(raw, kind)
    SCRIPT.write_bytes(lua.encode())
    print(f'Running {kind} in Mesen from {rom.name}, controller {H(lua.encode())}', flush=True)
    result = run(SCRIPT, rom, OUT / 'capture', CANDIDATE, 120)
    receipt = result['receipt']
    print('NATIVE ' + json.dumps({
        'kind': kind,
        'downloads': rom == ROM,
        **{key: result[key] for key in ('passed', 'returncode', 'script_SHA256', 'receipt_SHA256', 'seconds')},
        'receipt': receipt,
    }, separators=(',', ':')), flush=True)
    assert result['passed'] and result['outputs_written'] == 0 and not result['images']
    if kind == 'hud':
        hud = receipt['hud_continuity']
        underground = hud['buckets']['0:1:192']
        terminal = hud['terminal']
        assert hud['source_counter_only'] is False and terminal['area'] == 192
        assert terminal['NT2023'] == HUD_ROW, terminal
        assert terminal['cache'] == dict(health_low=16, health_high=25, ammo=5, dirty=0), terminal
        assert 0 < underground['packet_commits'] < underground['eligible'], underground
        assert 0 < underground['dirty_writes'] < underground['attempts'], underground
    assert_patch_free(rom, CANDIDATE)
    return result['receipt_SHA256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Install after private Mesen checks pass.')
    args = parser.parse_args()

    assert {entry.name for entry in OUT.iterdir()} == {CANDIDATE_ROM.name, SCRIPT.name}
    assert_patch_free(ROM, PARENT)
    parent = ROM.read_bytes()
    assert CANDIDATE_ROM.read_bytes() == parent
    previous_script = SCRIPT.read_bytes()
    capture_budget.preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    raw, scope = proposal(parent)
    print('COMPOSED ' + json.dumps(scope, separators=(',', ':')), flush=True)

    installed = False
    replacing_nightly = False
    try:
        CANDIDATE_ROM.write_bytes(raw)
        assert_patch_free(CANDIDATE_ROM, CANDIDATE)
        private = {kind: validate(CANDIDATE_ROM, raw, kind) for kind in KINDS}
        assert ROM.read_bytes() == parent
        assert_patch_free(ROM, PARENT)
        if args.install:
            replacing_nightly = True
            ROM.write_bytes(raw)
            assert ROM.read_bytes() == CANDIDATE_ROM.read_bytes() == raw
            assert_patch_free(ROM, CANDIDATE)
            actual = validate(ROM, raw, 'hud')
            assert actual == private['hud'], (actual, private['hud'])
            assert ROM.read_bytes() == raw
            installed = True
        print('DELIVERY ' + json.dumps({
            'installed': installed,
            'candidate_SHA256': CANDIDATE,
            'bytes': len(raw),
            'private_receipts': private,
            'downloads_hud_receipt': actual if installed else None,
        }, separators=(',', ':')), flush=True)
    finally:
        if not installed:
            if replacing_nightly:
                ROM.write_bytes(parent)
            CANDIDATE_ROM.write_bytes(parent)
            SCRIPT.write_bytes(previous_script)
            assert ROM.read_bytes() == parent


if __name__ == '__main__':
    main()
