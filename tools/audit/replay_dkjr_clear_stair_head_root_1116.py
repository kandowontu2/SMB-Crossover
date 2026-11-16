"""New ordinary stair inputs: retreat until the next step clears the head box."""
from hashlib import sha256

import replay_dkjr_ledge_vertical_hop_root_1116 as Previous


def controller(raw,*,source=False):
    text=Previous.controller(raw,source=source)
    edits=[('local riserAttempts=0','local riserAttempts=0\nlocal dkClearStair'),
        ('local lateSteps={{2127,176,true},{2142,160,true}',
         'local lateSteps={{2118,176,true},{2134,160,true}'),
        ('{2351,176,true},{2366,160,true}',
         '{2342,176,true},{2358,160,true}'),
        (" if phase=='late-walk'then\n  right=true", """ if phase=='late-walk'then
  if dkClearStair then
   local q=dkClearStair
   if riserTrace then
    riserTrace.min_y=math.min(riserTrace.min_y,y)
    riserTrace.max_x=math.max(riserTrace.max_x,player)
    riserTrace.airborne=riserTrace.airborne or not grounded
   end
   assert(updates-q.started<120,'Clear-head stair input bound')
   if not q.stopped then
    if player>q.x then bits=2;return end
    q.stopped=updates
   end
   local age=updates-q.stopped
   if age<4 then bits=0;return
   elseif age<12 then bits=129;return
   elseif grounded and read(0x1e)==0 and y==q.y then dkClearStair=nil
   else bits=1;return end
  end
  right=true"""),
        ('  if ready and step[3] then\n   assert(riserAttempts', """  if ready and step[3] and player>=takeoff then
   assert(riserAttempts<4,'Repeated clear-head stair preparation '..lateStep)
   dkClearStair={x=takeoff,y=step[2]-16,started=updates}
   riserStart,riserAttempts=updates,riserAttempts+1
   remember('clear-head-stair-'..lateStep)
   riserTrace=events[#events];riserTrace.min_y=y;riserTrace.max_x=player
   bits=player>takeoff and 2 or 0;return
  end
  if ready and step[3] then
   assert(riserAttempts""")]
    result=text
    for before,after in edits:
        assert result.count(before)==1,before
        result=result.replace(before,after,1)
    restored=result
    for before,after in reversed(edits):
        assert restored.count(after)==1
        restored=restored.replace(after,before,1)
    assert restored==text
    Previous.Frozen.Frozen.Frozen.Prior.Ground.LuaRuntime().compile(result)
    assert not any(w in result for w in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return result


if __name__=='__main__':
    from diagnose_dkjr_ledge_controls_root_1116 import execute
    execute(controller,limit=15000)
