"""Extend the qualified controller replay toward the third gap."""

from hashlib import sha256
import json
from pathlib import Path
import sys
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
  local riser=lateStep<=4 or lateStep>=6 and lateStep<=9
  if step and player>=step[1]-(riser and 3 or 0) and grounded and read(0x1e)==0 and y==step[2] then
   assert(player<=step[1]+2,'Missed late staircase takeoff')
   hold=updates+8;rearm=updates+47
   remember('late-jump-'..lateStep)
   lateStep=lateStep+1
  elseif not step and player>=2480 and grounded and read(0x1e)==0 and y==112 then
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
local nextLatePair=1
local latePairHolds={1840,1920}
local lateSteps={{2130,176},{2144,160},{2160,144},{2176,128},{2198,112},
                 {2354,176},{2368,160},{2384,144},{2400,128},{2438,112}}'''),
        ("   finish(true,'Four native DK Jr. pipe crossings, first gap and stock-assisted second gap')\n   return",
         "   setPhase('late-walk')"),
        (' bits=(right and 1 or 0)', THIRD_GAP_INPUT + ' bits=(right and 1 or 0)'),
        ("assert(frame<18000,'Physical bound')", "assert(frame<21000,'Physical bound')"),
    )
    for before, after in edits:
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    return source


def main(output):
    original = Delivery.SCRIPT.read_bytes()
    assert sha256(original).hexdigest() == Delivery.SCRIPT_PIN
    assert output.is_relative_to(Delivery.R / 'build') and output != Delivery.R / 'build'
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as directory:
        script = Path(directory) / 'dkjr_third_gap.lua'
        script.write_text(extend(original.decode('utf-8').replace('\r\n', '\n')),
                          encoding='utf-8')
        result = run(script, Delivery.NIGHTLY, output, Delivery.PIN, 180)
    q = result['receipt']
    print(json.dumps(dict(passed=result['passed'], SHA256=result['receipt_SHA256'],
                          script_SHA256=result['script_SHA256'], terminal=q['terminal'],
                          reason=q['reason'], injury=q.get('injury'),
                          events=[e for e in q['events'] if e['x'] >= 1424]), sort_keys=True),
          flush=True)
    assert result['passed']


if __name__ == '__main__':
    assert len(sys.argv) == 2
    main(Path(sys.argv[1]).resolve())
