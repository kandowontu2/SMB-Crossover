"""Run Prince through the original flagpole and into active underground 1-2."""

import argparse
import json
from pathlib import Path

import replay_prince_full_route_1111 as Route
from nightly_patch_guard_v1 import check


FLAG = Route.R / 'tools/playthroughs/prince_native_flag_1111.lua'


def controller(cookie, support_publication, brake=3097):
    source = Route.controller(cookie, support_publication)

    def change(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    change('local ending\n', 'local ending\n' + FLAG.read_text(encoding='utf-8') + '\n')
    change("  elseif progress=='late-finish-run' then\n", f"""  elseif progress=='late-finish-flag-brake' then
    if s.y_high==1 and s.y>=174 and s.y<=178 and idle(s) and s.action==0 then
      p.jumps[#p.jumps+1]={{kind='flag',request=s}}
      switch('late-finish-jump',128)
    elseif age>115 then
      error('Original flag approach did not settle before a fresh standing jump')
    end
  elseif progress=='late-finish-run' then
    if not p.flag_brake and x>={brake} and s.y>=174 and s.y<=178 and s.action==1 then
      p.flag_brake=s
      switch('late-finish-flag-brake',0)
      return
    end
""")
    return source


def replay(script, rom, output, pin):
    result = Route.replay(script, rom, output, pin)
    route = result['receipt']['later_route'].get('finish', {})
    if result['passed']:
        assert result['receipt']['controller_only'] and not result['receipt']['added_helpers']
        assert route['flag'] and route['castle'] and route['gap']
        terminal = result['receipt']['terminal']
        assert (terminal['world'], terminal['level'], terminal['engine'], terminal['lives']) == (0, 1, 8, 2)
    return result, route


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--expected', required=True)
    parser.add_argument('--cookie', required=True)
    parser.add_argument('--brake', type=int, default=3097)
    parser.add_argument('--support-publication', type=lambda value: int(value, 0), default=0xd74b)
    args = parser.parse_args()
    output, rom = args.output.resolve(), args.rom.resolve()
    assert output.is_relative_to(Route.R / 'build') and output != Route.R / 'build'
    assert check(rom)['ROM_sha256'] == args.expected
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(args.cookie, args.support_publication, args.brake),
                      encoding='utf-8', newline='\n')
    result, route = replay(script, rom, output / 'capture', args.expected)
    receipt = result['receipt']
    print(json.dumps(dict(passed=result['passed'], reason=receipt['reason'], phase=receipt['phase'],
                          terminal=receipt['terminal'], flag=route.get('flag'), castle=route.get('castle'),
                          flag_brake=route.get('flag_brake'), obstruction=route.get('obstruction'),
                          jump=route.get('jumps', [])[-1:] if route else [],
                          receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256']),
                     sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
