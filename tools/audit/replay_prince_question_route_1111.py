"""Test Prince's authored question-block climb and the live Goomba pair in Mesen."""

import argparse
import json
from pathlib import Path

import deliver_steve_move_1111 as Current
from nightly_patch_guard_v1 import check
import replay_prince_second_brick_1111 as Replay


def controller(cookie, support_publication, *, stock=False, neutral=False):
    source = Replay.controller(cookie, support_publication)

    def change(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    change('    local surface=s.y<=114', '    if s.action==10 then pad=0 end\n    local surface=s.y<=114')
    condition = '    if s.y<=114 and (support(s) or (surface and s.action==10)) and x+13>=1744 then'
    if stock:
        change(condition,
               '    local donorReady=s.mode==0 and s.pose==15 and x>=1744 and x<=1774\n'
               '    if s.y<=114 and (donorReady or support(s) or (surface and s.action==10)) and x+13>=1744 then')
    else:
        change(condition, '    if s.y==112 and support(s) and s.mode==0 and s.pose==15 and '
                          'tile(x+13,144)==0xc0 then')
    if neutral:
        change("      switch('late-chain-group-depart',128)",
               "      switch('late-chain-question-neutral',0)")
        target = "  elseif progress=='late-chain-group-depart' and s.action==3 then"
        change(target, """  elseif progress=='late-chain-question-neutral' then
    assert(s.y==112 and x==q.group.cap.x and support(s) and tile(x+13,144)==0xc0,
      'Original neutral pose stays grounded on the native question block')
    if commits-changedAt>=20 then
      q.group.neutral=s
      final=s
      finish(true,'Prince stays grounded on the exposed question block')
    end
""" + target)
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, default=Current.NIGHTLY)
    parser.add_argument('--expected', default=Current.PIN)
    parser.add_argument('--cookie', default=Current.Parent.COOKIE)
    parser.add_argument('--support-publication', type=lambda value: int(value, 0), default=0xd749)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--stock', action='store_true')
    mode.add_argument('--neutral', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Current.R / 'build') and output != Current.R / 'build'
    rom = args.rom.resolve()
    assert check(rom)['ROM_sha256'] == args.expected
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(args.cookie, args.support_publication, stock=args.stock, neutral=args.neutral),
                      encoding='utf-8', newline='\n')
    result = Replay.replay(script, rom, output / 'capture', args.expected, climb_group=True, climb_brake=1710)
    receipt = result['receipt']
    group = receipt['later_route'].get('chain', {}).get('group', {})
    print(json.dumps(dict(passed=result['passed'], reason=receipt['reason'], phase=receipt['phase'],
                          receipt=result['receipt_SHA256'], script=result['script_SHA256'],
                          group=group, terminal=receipt['terminal'], injuries=receipt['injuries']),
                     sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
