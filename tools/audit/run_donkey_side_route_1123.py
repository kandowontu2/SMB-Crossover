"""Replay the qualified classic Donkey Kong route against the side-probe change."""

import argparse
from copy import deepcopy
from functools import cache
from hashlib import sha256
import json

import check_contra_force_combined_palette_1122 as ContraPalette
import compose_battletoads_carry_current_1115 as Carry
import compose_battletoads_native_service_1114 as Service
import compose_bub_selected_star_palette_prince_1115 as BubStar
import compose_donkey_side_shortcut_1123 as Side
import compose_gimmick_empty_side_1115 as Gimmick
import compose_hot_draw_bt_67e_1115 as Draw
import compose_prince_body_transition_590_1115 as PrinceBody
import compose_prince_hidden_point67_ace_1115 as PrincePoint
import compose_prince_window567_1115 as PrinceWindow
import current_sonic_parent_rom_1122 as Sonic
import repair_contra_force_beans_ground_1122 as Beans
import replay_dk_earned_mushroom_full11_1114 as Replay
import run_roster_empty_cadence_current_1123 as Cadence


Native = Cadence.Previous
ROM = Native.Timing.ROM
REFERENCE_SCRIPT = '4601d3a2e38181a865436dda92101aa47f15bac56b58c382aaaacc3bea50289f'
# The main entry changed after the original replay. Its two fixed-bank
# callers are also used by the current cadence observer.
CURRENT_MAIN = {
    'GameLoop': (0x82D9, 'a9ff8d3901205983'),
    'GameLoopReturn0': (0x82BE, '68cd3a01f0ee20c4'),
    'GameLoopReturn1': (0x82D0, '68a9008d3b014cb2'),
}


def digest(data):
    return sha256(data).hexdigest()


@cache
def replay_reference(parent):
    """Recover the original fixture in memory through the exact ROM inverses."""
    assert digest(parent) == Side.PARENT
    foundation = Cadence.reference(parent)
    palette = ContraPalette.comparison_base(Beans.inverse(Sonic.inverse(foundation)))
    bridge = ContraPalette.Fast.Hud.inverse(palette)
    current = ContraPalette.Current
    battletoads, _ = current.Previous.reference(current.reference(bridge))
    for undo in (Draw.inverse, BubStar.inverse, PrincePoint.inverse, Carry.inverse,
                 Carry.reference_parent, Gimmick.current_inverse, PrinceBody.inverse,
                 PrinceWindow.inverse, Service.inverse):
        battletoads = undo(battletoads)
    assert digest(battletoads) == Replay.PIN
    return battletoads


def controller(reference, rom):
    text = Replay.controller(reference)
    assert digest(text.encode()) == REFERENCE_SCRIPT
    original = Replay.bindings(reference)
    q = deepcopy(original)
    changes = []
    for name, hook in q['hooks'].items():
        offset = 16 + hook['offset']
        expected = bytes(hook['bytes'])
        if name in CURRENT_MAIN:
            pc, signature = CURRENT_MAIN[name]
            assert hook['pc'] == pc and offset == 16 + 126 * 8192 + (pc & 8191)
            if name != 'GameLoop':
                assert rom[offset - 3:offset] == b'\x20\xd9\x82'
            expected = bytes.fromhex(signature)
            hook['bytes'] = list(expected)
        found = rom[offset:offset + len(expected)]
        if expected != found:
            changes.append((name, hex(offset), expected.hex(), found.hex()))
        if 'bank' in hook:
            at = 16 + hook['bank'] * 8192
            hook['bank_SHA256'] = digest(rom[at:at + 8192])
    assert not changes, changes
    q['sha'] = digest(rom)
    prefix = 'local C=' + Replay.Frozen.lua(original) + '\n'
    assert text.startswith(prefix)
    result = 'local C=' + Replay.Frozen.lua(q) + '\n' + text[len(prefix):]
    Replay.Frozen.LuaRuntime().compile(result)
    return result.encode()


def verify_route(script, rom, capture, expected):
    guard = Native.check(rom)
    assert guard['ROM_sha256'] == expected
    proof = Native.run(script, rom, capture, expected, 180, long_no_capture=True)
    assert Native.check(rom) == guard
    assert proof['outputs_written'] == 0 and not proof['images']
    q = proof['receipt']
    keys = ('passed', 'reason', 'physical_frames', 'actual_DkMovement_calls', 'flag', 'castle',
            'next_area_updates', 'terminal', 'natural_mushroom', 'actual_barrel_spawns', 'actual_injuries',
            'max_x', 'checkpoints')
    report = {key: q[key] for key in keys if key in q}
    report.update(ROM=expected, receipt_SHA256=proof['receipt_SHA256'], script_SHA256=proof['script_SHA256'])
    print('DONKEY SIDE ROUTE ' + json.dumps(report, separators=(',', ':')), flush=True)
    assert proof['passed'], q['reason']
    assert q['full_nonshortcut1_1'] and q['terminal']['level'] == 1 and q['next_area_updates'] == 25
    assert q['actual_barrel_spawns']['count'] > 0
    return proof['receipt_SHA256']


def run(*, install=False):
    installed_guard = Native.check(ROM)
    parent = ROM.read_bytes()
    assert installed_guard['ROM_sha256'] == Side.PARENT and not installed_guard['matching_patch_files']
    candidate, expected = Side.compose(parent)
    reference = replay_reference(parent)
    print(f'DONKEY SIDE REFERENCE {digest(reference)}', flush=True)
    scripts = [controller(reference, image) for image in (parent, candidate)]
    work = Native.Timing.SHARED
    rom, script = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, script} and rom.read_bytes() == parent
    Native.require_free_workspace(Native.Timing.R, ROM, allow_interactive=True)
    original_script = script.read_bytes()
    replaced = installed = False
    try:
        script.write_bytes(scripts[0])
        verify_route(script, rom, work / 'capture', Side.PARENT)
        rom.write_bytes(candidate)
        script.write_bytes(scripts[1])
        receipt = verify_route(script, rom, work / 'capture', expected)
        if install:
            assert Native.check(ROM) == installed_guard
            replaced = True
            ROM.write_bytes(candidate)
            assert verify_route(script, ROM, work / 'capture', expected) == receipt
            assert ROM.read_bytes() == candidate
            assert not Native.check(ROM)['matching_patch_files']
            installed = True
            print(f'Installed {expected} at {ROM}; matching Downloads replay {receipt}', flush=True)
    finally:
        if not installed:
            rom.write_bytes(parent)
            if replaced:
                ROM.write_bytes(parent)
            assert Native.check(ROM) == installed_guard
        script.write_bytes(original_script)
        assert set(work.iterdir()) == {rom, script}
        assert rom.read_bytes() == ROM.read_bytes() == (candidate if installed else parent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    run(install=parser.parse_args().install)
