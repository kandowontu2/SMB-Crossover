"""Try Prince's ordinary standing jump and second brick climb in actual Mesen."""

import argparse
import json
from pathlib import Path

import deliver_prince_brick_1111 as Delivery
from nightly_patch_guard_v1 import check
from replay_prince_koopa_1111 import published_controller, replace_once
from replay_steve_native_1111 import PIN as STEVE_PIN
from run_stdout_mesen_1110 import run


TAIL = Delivery.R / 'tools/playthroughs/prince_second_brick_1111.lua'


def controller():
    source = published_controller(Delivery.COOKIE)
    source = replace_once(source, r'local function afterSecondGap\(s\)',
                          TAIL.read_text(encoding='utf-8') + '\nlocal function afterSecondGap(s)\n'
                          "  if progress:sub(1,11)=='late-chain-' then throughSecondBrick(s);return end")
    return replace_once(source, r"      error\('Original jump fell short of the next brick'\)",
                        "      late.chain={entry=s}\n      switch('late-chain-recovery',1)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--goomba-gap', type=int, action='append', choices=range(0,151))
    parser.add_argument('--climb-group', action='store_true')
    parser.add_argument('--climb-brake', type=int, default=1700, choices=range(1685,1711))
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Delivery.R / 'build') and output != Delivery.R / 'build'
    pin = check(Delivery.NIGHTLY)['ROM_sha256']
    assert pin in (Delivery.PIN, STEVE_PIN)
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(), encoding='utf-8', newline='\n')
    for gap in args.goomba_gap or (0,):
        result = run(script, Delivery.NIGHTLY, output / 'capture', pin, 120, variant=3,
                     extra_env={'SMB_PRINCE_KOOPA_BRAKE': '1470', 'SMB_PRINCE_KOOPA_MODE': 'air',
                                'SMB_PRINCE_GOOMBA_GAP': str(gap),
                                'SMB_PRINCE_GOOMBA_BRAKE': str(args.climb_brake),
                                'SMB_PRINCE_GOOMBA_CLIMB': '1' if args.climb_group else '0'})
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
