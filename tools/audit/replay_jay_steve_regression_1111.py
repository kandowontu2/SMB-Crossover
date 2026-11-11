"""Recheck the full Jay route with a running approach to the final stair."""

import argparse
import json
from pathlib import Path

import deliver_jay_silius_1111 as Jay
import replay_steve_native_1111 as Steve


FINAL_STAIR = '''
 if late.finalStair=='backup' then
  if x<=2890 and grounded then
   late.finalStair='jump';late.hold=entries+14
   jumps[#jumps+1]=string.format('[%d,%d,%d,14,"final-stair-runup"]',entries,x,y)
   bits=129
  else
   bits=2
  end
  return
 elseif not late.finalStair and x>=2893 and x<=2901 and y==144 and grounded
   and entries-late.advanced>=55 then
  late.finalStair='backup';bits=2
  return
 end
'''


def controller():
    source = Jay.SCRIPT.read_text(encoding='utf-8')
    line = ' local grounded=ram(2,donorFlags-0xc000)&4==0\n'
    assert source.count(line) == 1
    return source.replace(line, line + FINAL_STAIR)


def replay(rom, output, script):
    return Steve.run(script, rom, output, Steve.PIN, 120, variant=2,
                     extra_env={'SMB_JAY_COOKIE': Steve.COOKIE, 'SMB_JAY_DONOR_FLAGS': '49170'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(Jay.R / 'build') and output != Jay.R / 'build'
    output.mkdir(exist_ok=True)
    script = output / 'jay.lua'
    script.write_text(controller(), encoding='utf-8', newline='\n')
    result = replay(args.rom.resolve(), output / 'capture', script)
    receipt = result['receipt']
    print(json.dumps(dict(passed=result['passed'], receipt_SHA256=result['receipt_SHA256'],
        script_SHA256=result['script_SHA256'], result={key: receipt[key] for key in (
            'reason', 'physical_frames', 'scroll_entries', 'dma_matches', 'late_jumps',
            'flag', 'castle', 'three_way', 'lives', 'x', 'y')}), sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
