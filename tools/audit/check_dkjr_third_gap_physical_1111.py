"""Extend the qualified controller replay toward the third gap."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import deliver_dkjr_second_gap_1111 as Delivery
from run_stdout_mesen_1110 import run


THIRD_GAP_INPUT = """
 if phase=='late-walk'then
  right=true
  local pairHold=latePairHolds[nextLatePair]
  local waitingForPair=pairHold and player>=pairHold and player<pairHold+12
  if waitingForPair then right=false end
  local step=lateSteps[lateStep]
  local settled=grounded and read(0x1e)==0
  if riserTrace then
   riserTrace.min_y=math.min(riserTrace.min_y,y)
   riserTrace.max_x=math.max(riserTrace.max_x,player)
   riserTrace.airborne=riserTrace.airborne or not settled
  end
  if riserStart and settled and y==step[2]-16 then
   remember('late-land-'..lateStep)
   lateStep=lateStep+1
   riserStart,riserTrace,riserAttempts=nil,nil,0
   step=lateSteps[lateStep]
  end
  local ready=step and settled and y==step[2] and (not riserStart or updates-riserStart>=47)
  local retries=step and step[4]
  local takeoff=step and (retries and retries[riserAttempts+1] or step[1])
  if ready and step[3] then
   assert(riserAttempts<(retries and #retries or 4),'No height gained on late riser '..lateStep)
  end
  if ready and retries and riserAttempts>0 and player>takeoff then
   right,left=false,true
  elseif ready and player>=takeoff then
   assert(player<=takeoff+6,'Missed late staircase takeoff')
   hold=updates+8;rearm=updates+47
   remember('late-jump-'..lateStep)
   if step[3] then
    riserStart,riserAttempts=updates,riserAttempts+1
    riserTrace=events[#events];riserTrace.min_y=y;riserTrace.max_x=player
   else
    lateStep=lateStep+1
   end
  elseif not step and player>=2480 and settled and y==112 then
   setPhase('far-third-gap-bank')
   finish(true,'All three gaps and four opening pipes')
   return
  elseif (not step or player<step[1]-30) and grounded and updates>=rearm then
   for _,actor in ipairs(approachActors())do
    local dx=actor[3]-player
    local range=actor[2]==6 and nextLatePair~=2 and 30 or 40
    if actor[2]<=6 and actor[4]>=172 and actor[5]&32==0 and dx>=8 and dx<=range then
     if waitingForPair then nextLatePair=nextLatePair+1;right=true end
     hold=updates+8;rearm=updates+47;remember('late-enemy-hop')
     events[#events].actors=approachActors()
     break
    end
   end
  end
 end
"""


def extend(source):
    edits = (
        ('local pendingPlane', '''local pendingPlane
local lateStep=1
local riserStart,riserTrace
local riserAttempts=0
local nextLatePair=1
local latePairHolds={1840,1920}
local lateSteps={{2127,176,true},{2142,160,true},{2150,144,true,{2150,2155,2153,2157}},
                 {2166,128,true,{2166,2171,2169,2173}},{2198,112},
                 {2351,176,true},{2366,160,true},{2374,144,true,{2374,2379,2377,2381}},
                 {2390,128,true,{2390,2395,2393,2397}},{2438,112}}'''),
        ("   finish(true,'Four native DK Jr. pipe crossings, first gap and stock-assisted second gap')\n   return",
         "   setPhase('late-walk')"),
        (' bits=(right and 1 or 0)', THIRD_GAP_INPUT + ' bits=(right and 1 or 0)'),
        ("assert(frame<18000,'Physical bound')", "assert(frame<21000,'Physical bound')"),
    )
    for before, after in edits:
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    return source


def main(output, rom, expected):
    original = Delivery.SCRIPT.read_bytes()
    assert sha256(original).hexdigest() == Delivery.SCRIPT_PIN
    assert output.is_relative_to(Delivery.R / 'build') and output != Delivery.R / 'build'
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as directory:
        script = Path(directory) / 'dkjr_third_gap.lua'
        script.write_text(extend(original.decode('utf-8').replace('\r\n', '\n')),
                          encoding='utf-8')
        result = run(script, rom, output, expected, 180)
    q = result['receipt']
    print(json.dumps(dict(passed=result['passed'], SHA256=result['receipt_SHA256'],
                          script_SHA256=result['script_SHA256'], terminal=q['terminal'],
                          reason=q['reason'], injury=q.get('injury'),
                          events=[e for e in q['events'] if e['x'] >= 1424]), sort_keys=True),
          flush=True)
    assert result['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--rom', type=Path, default=Delivery.NIGHTLY)
    parser.add_argument('--expected', default=Delivery.PIN)
    args = parser.parse_args()
    main(args.output.resolve(), args.rom, args.expected)
