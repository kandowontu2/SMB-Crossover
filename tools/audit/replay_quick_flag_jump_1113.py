"""Jump over the native flag-base block; retain the frozen Quick item route."""

import argparse
from hashlib import sha256
import json

import check_quick_powerups_current_1113 as Q
from run_stdout_mesen_1110 import run


def controller(raw):
    text=Q.controller(raw,'full')
    before='  if x<3156 then return 1+b end'
    assert text.count(before)==1
    text=text.replace(before,"  if x>=3136 and x<3170 then return 1+jump()end\n"+before)
    before='local function control()\n'
    assert text.count(before)==1
    text=text.replace(before,before+" if r('LevelNumber')==1 then return 0 end\n")
    before="if MODE=='full'and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 then finish(true,'full-1-1');return end"
    assert text.count(before)==1
    text=text.replace(before,"if MODE=='full'and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 and r('Player_State')==0 and r('Player_Y_Position')==176 and r('Player_Y_HighPos')==1 then finish(true,'full-1-1-grounded-1-2');return end")
    before="or r('QmField_06C0')==0 then finish(false,'life-lost')"
    assert text.count(before)==1
    # The next room's forced-blank constructor invalidates source WRAM.
    # Health is meaningful in active gameplay, after its cold publication.
    return text.replace(before,"or(r('GameEngineSubroutine')==8 and r('QmField_06C0')==0)then finish(false,'life-lost')")


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',action='store_true')
    args=parser.parse_args()
    out=Q.R/'build/metal-flower-native-1112'
    rom=Q.C.ROM if args.baseline else out/'candidate.nes'
    raw=rom.read_bytes()
    assert sha256(raw).hexdigest() in (Q.PIN,'4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3')
    script=out/'controller.lua'
    script.write_text(controller(raw),encoding='utf-8',newline='\n')
    r=run(script,rom,out/'capture',sha256(raw).hexdigest(),180)
    q=r['receipt']
    print(json.dumps(dict(passed=r['passed'],receipt_SHA256=r['receipt_SHA256'],
        script_SHA256=r['script_SHA256'],ROM_SHA256=r['ROM_SHA256'],reason=q['reason'],
        terminal=q['terminal'],stage_events=q.get('stage_events'),pickup_count=len(q['pickups']))),flush=True)
