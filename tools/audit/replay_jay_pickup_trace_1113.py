"""Read-only trace of the native Jay pickup replay, without control changes."""

from hashlib import sha256
import argparse
import json

import replay_jay_powerups_1113 as Q


def controller(raw, runup_x=None):
    text = Q.controller(raw, expect='earned')
    assert sha256(text.encode()).hexdigest() == '8e72af806023c5aed04368a39b2e8112c0c48690b47853d600fdce41a5e178b0'
    edits = (
        ('local registered={}', 'local registered={}\nlocal routeTrace={}\nlocal priorTracePhase=nil'),
        ('minimum_y=minimum,block=r(0x445),trace=trace}',
         'minimum_y=minimum,block=r(0x445),trace=trace,route_trace=routeTrace,phase=phase}'),
        (' local shot=near and epoch%12<2 and 64 or 0', ''' if phase~=priorTracePhase or(epoch%4==0 and epoch<420)then
  priorTracePhase=phase
  assert(#routeTrace<128,'Bounded diagnostic trace')
  routeTrace[#routeTrace+1]={phase=phase,age=epoch-phaseEpoch,pad=pad,player=s,item=item or false}
 end
 local shot=near and epoch%12<2 and 64 or 0'''),
    )
    for before, after in edits:
        assert text.count(before) == 1
        text = text.replace(before, after)
    if runup_x is not None:
        assert 409<=runup_x<=448
        before="""   if s.source_flags&2~=0 then phaseTo('collect-jump');pad=130+shot
   else phaseTo('pipe-face');pad=2+shot end"""
        assert text.count(before)==1
        text=text.replace(before,"   phaseTo('pipe-runup');pad=2+shot")
        before="if epoch-phaseEpoch>=1 and s.source_flags&4==0 then phaseTo('collect-jump');pad=pad|128 end"
        assert text.count(before)==1
        text=text.replace(before,f"if s.x<={runup_x} and s.motion==0 and s.y==144 then phaseTo('collect-jump');pad=pad|128 end")
    return text


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runup-x',type=int)
    args=parser.parse_args()
    out = Q.R/'build/metal-flower-native-1112'
    rom, script = out/'candidate.nes', out/'controller.lua'
    raw = rom.read_bytes()
    script.write_text(controller(raw,args.runup_x), encoding='utf-8', newline='\n')
    r = Q.run(script, rom, out/'capture', sha256(raw).hexdigest(), 180)
    receipt = r['receipt']
    print(json.dumps(dict(passed=r['passed'], receipt_SHA256=r['receipt_SHA256'],
        script_SHA256=r['script_SHA256'], phase=receipt['phase'], terminal=receipt['terminal'],
        route_trace=[v for v in receipt['route_trace'] if 250<=v['player']['epoch']<=350],
        births=receipt['births'], collections=receipt['collections'])), flush=True)
