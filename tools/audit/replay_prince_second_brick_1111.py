"""Try Prince's ordinary standing jump and second brick climb in actual Mesen."""

import argparse
import json
from pathlib import Path
import re

import deliver_prince_brick_1111 as Delivery
from nightly_patch_guard_v1 import check
from replay_prince_koopa_1111 import published_controller, replace_once
from replay_steve_native_1111 import PIN as STEVE_PIN
from run_stdout_mesen_1110 import run


TAIL = Delivery.R / 'tools/playthroughs/prince_second_brick_1111.lua'


def controller(cookie=Delivery.COOKIE, support_publication=0xd74b):
    source = published_controller(cookie)
    assert 0xd6d1 <= support_publication <= 0xd753
    source, count = re.subn(r'0xd74[b-d]', lambda match: hex(
        support_publication + int(match[0], 16) - 0xd74b), source)
    assert count == 4
    source = replace_once(source, r'local function afterSecondGap\(s\)',
                          TAIL.read_text(encoding='utf-8') + '\nlocal function afterSecondGap(s)\n'
                          "  if progress:sub(1,11)=='late-chain-' then throughSecondBrick(s);return end")
    return replace_once(source, r"      error\('Original jump fell short of the next brick'\)",
                        "      late.chain={entry=s}\n      switch('late-chain-recovery',1)")


def replay(script, rom, output, pin, *, hold_on_cap=False, goomba_gap=0,
           climb_group=False, climb_brake=1700, climb_nudge=0, climb_step=False,
           backtrack_group=False, backtrack_brake=1652, backtrack_start=1670):
    result = run(script, rom, output, pin, 120, variant=3,
                 extra_env={'SMB_PRINCE_KOOPA_BRAKE': '1470', 'SMB_PRINCE_KOOPA_MODE': 'air',
                            'SMB_PRINCE_GOOMBA_GAP': str(goomba_gap),
                            'SMB_PRINCE_GOOMBA_BRAKE': str(climb_brake),
                            'SMB_PRINCE_GOOMBA_NUDGE': str(climb_nudge),
                            'SMB_PRINCE_GOOMBA_STEP': str(int(climb_step)),
                            'SMB_PRINCE_SECOND_BRICK_HOLD': str(int(hold_on_cap)),
                            'SMB_PRINCE_BACKTRACK_GROUP': str(int(backtrack_group)),
                            'SMB_PRINCE_BACKTRACK_BRAKE': str(backtrack_brake),
                            'SMB_PRINCE_BACKTRACK_START': str(backtrack_start),
                            'SMB_PRINCE_GOOMBA_CLIMB': str(int(climb_group))})
    if result['passed'] and hold_on_cap:
        receipt = result['receipt']
        chain = receipt['later_route']['chain']
        assert receipt['controller_only'] and not receipt['added_helpers']
        assert receipt['terminal']['commit'] - chain['cap']['commit'] >= 20
        assert chain['support_entries'] and chain['support_writes']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--goomba-gap', type=int, action='append', choices=range(0,151))
    parser.add_argument('--climb-group', action='store_true')
    parser.add_argument('--climb-brake', type=int, default=1700, choices=range(1685,1711))
    parser.add_argument('--climb-nudge', type=int, default=0, choices=range(0,13))
    parser.add_argument('--climb-step', action='store_true')
    parser.add_argument('--hold-on-cap', action='store_true')
    parser.add_argument('--backtrack-group', action='store_true')
    parser.add_argument('--backtrack-brake', type=int, default=1652, choices=range(1630,1680))
    parser.add_argument('--backtrack-start', type=int, default=1670, choices=range(1660,1720))
    parser.add_argument('--rom', type=Path, default=Delivery.NIGHTLY)
    parser.add_argument('--expected')
    parser.add_argument('--cookie', default=Delivery.COOKIE)
    parser.add_argument('--support-publication', type=lambda value: int(value, 0), default=0xd74b)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Delivery.R / 'build') and output != Delivery.R / 'build'
    rom = args.rom.resolve()
    pin = check(rom)['ROM_sha256']
    if args.expected:
        assert pin == args.expected
    else:
        assert rom == Delivery.NIGHTLY.resolve() and pin in (Delivery.PIN, STEVE_PIN)
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(args.cookie, args.support_publication), encoding='utf-8', newline='\n')
    for gap in args.goomba_gap or (0,):
        result = replay(script, rom, output / 'capture', pin,
                        hold_on_cap=args.hold_on_cap, goomba_gap=gap,
                        climb_group=args.climb_group, climb_brake=args.climb_brake,
                        climb_nudge=args.climb_nudge, climb_step=args.climb_step,
                        backtrack_group=args.backtrack_group, backtrack_brake=args.backtrack_brake,
                        backtrack_start=args.backtrack_start)
        receipt = result['receipt']
        chain = receipt['later_route'].get('chain', {})
        if gap and 'group' in chain:
            group = chain['group']
            if 'samples' in group:
                group['samples'] = group['samples'][-3:]
            chain = dict(far_side=chain['far_side'], group=group)
        print(json.dumps(dict(passed=result['passed'], goomba_gap=gap, reason=receipt['reason'],
            phase=receipt['phase'], receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'],
            terminal=receipt['terminal'], chain=chain), sort_keys=True), flush=True)
        if result['passed']:
            break
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
