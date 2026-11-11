"""Replay DK Jr.'s complete World 1-1 route on a pinned MMC5 ROM."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import check_dkjr_third_gap_physical_1111 as Third
from run_stdout_mesen_1110 import run


Delivery = Third.Delivery
DRIVER = Delivery.R / 'tools/playthroughs/dkjr_late_stage_driver_1111.lua'

STAGE_EXIT = """
 if phase=='late-flag'then
  local level,engine=read(0x761),read(0x0f)
  if level==0 and engine==4 and x()>=3140 and not flagResult then flagResult=snapshot()end
  if level==0 and engine==5 and x()>=3160 and not castleResult then castleResult=snapshot()end
  if level==1 and engine==7 and not entranceResult then entranceResult=snapshot()end
  if level==1 and active() and read(0x753)==2 and read(0x764)==0 then
   assert(flagHop and flagResult and castleResult and entranceResult and read(0x75f)==2,
    'Complete native flagpole, castle and 1-2 entrance')
   for i=9,#lifts do
    local key=tostring(lifts[i]);assert(births[key] and visible[key] and carries[key] and carries[key].count>0,
     'Missing late stock actor witness '..key)
   end
   setPhase('active-underground-1-2')
   finish(true,'Donkey Kong Jr. cleared 1-1 and entered active 1-2')
   return
  end
  if engine~=8 or level~=0 then bits=0;return end
 end
"""


def compose(original, driver, cookie, constructor):
    assert 0xc000 <= constructor < 0xe000
    edits = (
        ("local lifts={416,480,560,624,688,752,880,944}",
         "local lifts={416,480,560,624,688,752,880,944,2576,2640,2832,3040}"),
        ("[880]=161,[944]=161}", "[880]=161,[944]=161,[2576]=177,[2640]=128,[2832]=177,[3040]=128}"),
        ("local pendingPlane", """local pendingPlane
local thirdGap,flagHop,flagResult,castleResult,entranceResult
local finalRiser,finalRiserStart,finalRiserAttempts=1,nil,0
local finalWaitX,finalWaitStart
local finalLaunches={{2912,2912,2907},{2923,2928,2925},{2939,2944,2941},
                     {2955,2960,2957},{2971,2976,2973},{2987,2992,2989}}"""),
        ("assert(#events<100", "assert(#events<160"),
        ("phase=phase,pipe=index}", """phase=phase,pipe=index,
  world=read(0x764),level=read(0x761),area_type=read(0x753),mode=read(0x771),task=read(0x773),
  timer=100*read(0x7bf)+10*read(0x7c0)+read(0x7c1)}"""),
        ("first_gap=firstGap,second_gap=gap", """first_gap=firstGap,second_gap=gap,third_gap=thirdGap,
  flag=flagResult,castle=castleResult,entrance=entranceResult"""),
        ("local function drive()\n", "local function drive()\n" + STAGE_EXIT),
        ("   for _,left in ipairs(lifts)do\n    local key=", "   for i=1,8 do\n    local left=lifts[i];local key="),
        ("   finish(true,'All three gaps and four opening pipes')\n   return",
         "   thirdGap=snapshot();setPhase('pipe5-approach')"),
        (" bits=(right and 1 or 0)", driver + "\n bits=(right and 1 or 0)"),
        ("a72801b96058ad9af823ba7f575bf9d0", cookie),
        ("mapped(0xd1ea,'nesWorkRam',2*8192+0x11ea)",
         f"mapped(0x{constructor:x},'nesWorkRam',2*8192+0x{constructor-0xc000:x})"),
        ("end),emu.callbackType.exec,0xd1ea)", f"end),emu.callbackType.exec,0x{constructor:x})"),
        ("assert(frame<21000,'Physical bound')", "assert(frame<34000,'Physical bound')"),
    )
    source = Third.extend(original)
    for before, after in edits:
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    return source


def replay(rom, expected, output, constructor):
    raw = rom.read_bytes()
    assert sha256(raw).hexdigest() == expected
    offset = Delivery.Gap.Four.COOKIE_AT
    cookie = raw[offset:offset+16].hex()
    assert cookie.startswith('a72801')
    original = Delivery.SCRIPT.read_bytes()
    assert sha256(original).hexdigest() == Delivery.SCRIPT_PIN
    assert output.is_relative_to(Delivery.R / 'build') and output != Delivery.R / 'build'
    output.mkdir(parents=True, exist_ok=True)
    source = compose(original.decode('utf-8').replace('\r\n', '\n'),
                     DRIVER.read_text(encoding='utf-8'), cookie, constructor)
    with TemporaryDirectory(dir=output) as directory:
        script = Path(directory) / 'dkjr_full_stage.lua'
        script.write_text(source, encoding='utf-8')
        return run(script, rom, output, expected, 240)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--expected', required=True)
    parser.add_argument('--constructor', type=lambda s: int(s, 0), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.rom, args.expected, args.output.resolve(), args.constructor)
    q = result['receipt']
    print(json.dumps(dict(passed=result['passed'], SHA256=result['receipt_SHA256'],
                          script_SHA256=result['script_SHA256'], terminal=q['terminal'],
                          reason=q['reason'], injury=q.get('injury'),
                          third_gap=q.get('third_gap'), flag=q.get('flag'), castle=q.get('castle'),
                          entrance=q.get('entrance'), births=q['births'], visible=q['visible'],
                          events=[event for event in q['events'] if event['x'] >= 2120]),
                     sort_keys=True), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
