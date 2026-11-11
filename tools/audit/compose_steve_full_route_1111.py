"""Assemble the controller-only Mesen replay for Steve's complete stock 1-1."""

import argparse
import json
from pathlib import Path

import deliver_steve_move_1111 as Delivery
from nightly_patch_guard_v1 import check


TAIL = Delivery.R / 'tools/playthroughs/steve_native_full_route_1111.lua'


def controller():
    source = Delivery.Replay.controller()

    def change(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    change('local motionCalls,projections,crouchUpdates,jumpUpdates,wallX,apex',
           'local motionCalls,projections,crouchUpdates,jumpUpdates,wallX,apex\n'
           'local full,beginFull,fullTick')
    change('"wall_x":%d,"apex_y":%d}',
           '"wall_x":%d,"apex_y":%d,"flag":%s,"castle":%s,"hp":%d,'
           '"route_crossings":[%s],"route_jumps":[%s]}')
    change('motionCalls,projections,crouchUpdates,jumpUpdates,wallX,apex))',
           'motionCalls,projections,crouchUpdates,jumpUpdates,wallX,apex,'
           'tostring(full and full.flag or false),tostring(full and full.castle or false),read(0x5f30),'
           'full and table.concat(full.crossings,",") or "",full and table.concat(full.jumps,",") or ""))')
    continuation = TAIL.read_text(encoding='utf-8')
    for name in ('full', 'function beginFull', 'function fullTick'):
        start = 'local ' + name
        replacement = name if name == 'full' else name.removeprefix('function ') + ' = function'
        assert continuation.count(start) == 1, start
        continuation = continuation.replace(start, replacement)
    change("      finish(true,'Steve punches the first Goomba and clears the first pipe with original movement')",
           "      phase='motion-full';beginFull()")
    change('local function tick()', continuation + '\nlocal function tick()\n'
           "  if phase=='motion-full' then fullTick();return end")
    change("assert(frame<=4200,'Bounded physical Steve replay')",
           "assert(frame<=8500,'Bounded physical Steve replay')")
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Delivery.R / 'build') and output != Delivery.R / 'build'
    assert check(Delivery.NIGHTLY)['ROM_sha256'] == Delivery.PIN
    installed = Delivery.NIGHTLY.read_bytes()
    image, program, punch, cookie = Delivery.proposal(Delivery.recover_parent(installed))
    assert image == installed
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(), encoding='utf-8', newline='\n')
    result = Delivery.Replay.replay(script, Delivery.NIGHTLY, output / 'capture',
                                    Delivery.PIN, program, punch, cookie)
    print(json.dumps(dict(passed=result['passed'], receipt=result['receipt'],
                          receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256']),
                     sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
