"""Physically test Steve's original motion and punch on a rebased MMC5 candidate."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_steve_shatterhand_move_live_1111 as Source
import deliver_prince_exposed_brick_idle_1111 as Parent
from nightly_patch_guard_v1 import check
import replay_steve_native_1111 as Punch
from run_stdout_mesen_1110 import run


TAIL = Parent.R / 'tools/playthroughs/steve_native_move_1111.lua'


def controller():
    text = Punch.SCRIPT.read_text(encoding='utf-8')

    def change(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    change('local expected,pending={},{}', 'local expected,pending={},{}\n'
           'local motionCalls,projections,crouchUpdates,jumpUpdates,wallX,apex')
    change('"enemy_slot":%d,"enemy_state":%d,"score":%d,"dma_matches":%d}',
           '"enemy_slot":%d,"enemy_state":%d,"score":%d,"dma_matches":%d,'
           '"motion_calls":%d,"projections":%d,"crouch_frames":%d,"jump_updates":%d,'
           '"wall_x":%d,"apex_y":%d}')
    change('read(0x10d+slot),dmaMatches))', 'read(0x10d+slot),dmaMatches,'
           'motionCalls,projections,crouchUpdates,jumpUpdates,wallX,apex))')
    continuation = TAIL.read_text(encoding='utf-8')
    change('local function tick()', continuation + '\nlocal function tick()\n'
           "  if phase:sub(1,7)=='motion-' then moveTick();return end")
    change("      finish(true,'Steve held B and naturally defeated the first Goomba')",
           "      phase='motion-crouch';motionStart=updates;pad=4")
    change('select=pad&32~=0,b=pad&64~=0}', 'select=pad&32~=0,b=pad&64~=0,a=pad&128~=0}')
    return text


def replay(script, rom, output, expected, program, punch, cookie):
    return run(script, rom, output, expected, 120, extra_env={
        'SMB_STEVE_COOKIE': cookie.hex(),
        'SMB_STEVE_BIRTH': str(punch['symbols']['StevePunchBirth']),
        'SMB_STEVE_DRAW': str(punch['symbols']['SteveDrawEmit']),
        'SMB_STEVE_MOVE_ENTRY': str(program['symbols']['SteveLiveMovement']),
        'SMB_STEVE_MOVE_PROJECT': str(program['symbols']['SteveMotionProject']),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected', required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Parent.R / 'build') and output != Parent.R / 'build'
    assert check(Parent.NIGHTLY)['ROM_sha256'] == Parent.PIN
    current = Parent.NIGHTLY.read_bytes()
    raw = Parent.recover_parent(current)
    candidate, program, punch, cookie = Source.proposal(raw)
    rebased, _ = Parent.Source.replace_workers(candidate, *Parent.Source.source_workers())
    assert sha256(rebased).hexdigest() == args.expected
    output.mkdir(exist_ok=True)
    rom = output / 'candidate.nes'
    if rom.exists():
        assert rom.read_bytes() == rebased
    else:
        rom.write_bytes(rebased)
    script = output / 'controller.lua'
    script.write_text(controller(), encoding='utf-8', newline='\n')
    result = replay(script, rom, output / 'capture', args.expected, program, punch, cookie)
    print(json.dumps(result, sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
